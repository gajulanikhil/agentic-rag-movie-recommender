import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import re

class MovieDataProcessor:
    def __init__(self, raw_data_path: str = 'data/raw', processed_data_path: str = 'data/processed'):
        self.raw_path = Path(raw_data_path)
        self.processed_path = Path(processed_data_path)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
    def clean_text(self, text: str) -> str:
        """Clean text data"""
        if pd.isna(text):
            return ""
        text = str(text)
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        text = text.strip()
        return text
    
    def parse_json_column(self, json_str: str, key: str = 'name') -> List[str]:
        """Parse JSON string column and extract values"""
        try:
            if pd.isna(json_str):
                return []
            data = json.loads(json_str)
            return [item[key] for item in data if key in item]
        except:
            return []
    
    def process_netflix_data(self) -> pd.DataFrame:
        """Process Netflix dataset"""
        df = pd.read_csv(self.raw_path / 'netflix_titles.csv')
        
        # Clean text fields
        df['title'] = df['title'].apply(self.clean_text)
        df['description'] = df['description'].apply(self.clean_text)
        df['director'] = df['director'].apply(self.clean_text)
        df['cast'] = df['cast'].apply(self.clean_text)
        
        # Split genres
        df['genres'] = df['listed_in'].str.split(', ')
        
        # Filter movies only (optional - remove if you want TV shows too)
        movies_df = df[df['type'] == 'Movie'].copy()
        
        return movies_df
    
    def process_tmdb_data(self) -> pd.DataFrame:
        """Process TMDB dataset"""
        movies = pd.read_csv(self.raw_path / 'tmdb_5000_movies.csv')
        credits = pd.read_csv(self.raw_path / 'tmdb_5000_credits.csv')
        
        # Merge datasets
        df = movies.merge(credits, on='title', how='left')
        
        # Parse JSON columns
        df['genres_list'] = df['genres'].apply(lambda x: self.parse_json_column(x))
        df['cast_list'] = df['cast'].apply(lambda x: self.parse_json_column(x))
        df['director_list'] = df['crew'].apply(
            lambda x: [item['name'] for item in json.loads(x) if item.get('job') == 'Director'] if pd.notna(x) else []
        )
        
        # Clean overview
        df['overview'] = df['overview'].apply(self.clean_text)
        
        # Filter quality content
        quality_df = df[
            (df['vote_average'] >= 6.0) & 
            (df['vote_count'] >= 500) &
            (df['overview'].str.len() > 50)
        ].copy()
        
        return quality_df
    
    def merge_datasets(self, netflix_df: pd.DataFrame, tmdb_df: pd.DataFrame) -> pd.DataFrame:
        """Merge Netflix and TMDB data"""
        # Standardize column names for merging
        netflix_subset = netflix_df[['title', 'description', 'release_year', 'genres', 'director', 'cast']].copy()
        netflix_subset['source'] = 'netflix'
        
        tmdb_subset = tmdb_df[['title', 'overview', 'release_date', 'genres_list', 'director_list', 'cast_list', 'vote_average', 'runtime']].copy()
        tmdb_subset['source'] = 'tmdb'
        tmdb_subset['release_year'] = pd.to_datetime(tmdb_subset['release_date'], errors='coerce').dt.year
        
        # Rename for consistency
        netflix_subset.rename(columns={'description': 'overview'}, inplace=True)
        tmdb_subset.rename(columns={
            'genres_list': 'genres',
            'director_list': 'director',
            'cast_list': 'cast'
        }, inplace=True)
        
        # Select common columns
        common_cols = ['title', 'overview', 'release_year', 'genres', 'director', 'cast', 'source']
        netflix_final = netflix_subset[common_cols]
        
        tmdb_common = tmdb_subset[common_cols + ['vote_average', 'runtime']]
        
        # Combine
        combined_df = pd.concat([tmdb_common, netflix_final], ignore_index=True)
        
        # Remove duplicates based on title
        combined_df = combined_df.drop_duplicates(subset=['title'], keep='first')
        
        return combined_df
    
    def create_movie_documents(self, df: pd.DataFrame, num_docs: int = 15) -> List[Dict]:
        """Create rich document entries for top movies"""
        documents = []
        
        # Sort by vote_average if available, otherwise just take first N
        if 'vote_average' in df.columns:
            top_movies = df.nlargest(num_docs, 'vote_average')
        else:
            top_movies = df.head(num_docs)
        
        for idx, row in top_movies.iterrows():
            # Extract data
            title = row['title']
            overview = row['overview']
            year = row['release_year']
            genres = row['genres'] if isinstance(row['genres'], list) else []
            director = row['director'] if pd.notna(row['director']) else 'Unknown'
            #cast = row['cast'] if pd.notna(row['cast']) else 'Unknown'
            cast = row['cast'] if isinstance(row['cast'], list) and len(row['cast']) > 0 else 'Unknown'
            
            # Format cast/director
            if isinstance(cast, list):
                cast_str = ', '.join(cast[:5])  # Top 5 actors
            else:
                cast_str = str(cast)
            
            if isinstance(director, list):
                director_str = ', '.join(director)
            else:
                director_str = str(director)
            
            # Format genres
            if isinstance(genres, list):
                genres_str = ', '.join(genres)
            else:
                genres_str = str(genres)
            
            # Create document text
            doc_text = f"""# {title} ({year})

**Genres**: {genres_str}
**Director**: {director_str}
**Cast**: {cast_str}

## Overview
{overview}

## Key Information
- Release Year: {year}
- Type: Movie
"""
            
            # Add rating if available
            if 'vote_average' in row and pd.notna(row['vote_average']):
                doc_text += f"- Rating: {row['vote_average']}/10\n"
            
            if 'runtime' in row and pd.notna(row['runtime']):
                doc_text += f"- Runtime: {row['runtime']} minutes\n"
            
            # Create metadata
            metadata = {
                'title': title,
                'year': int(year) if pd.notna(year) else None,
                'genres': genres if isinstance(genres, list) else genres_str.split(', '),
                'director': director_str,
                'source': row['source']
            }
            
            documents.append({
                'content': doc_text,
                'metadata': metadata
            })
        
        return documents
    
    def create_genre_documents(self, df: pd.DataFrame) -> List[Dict]:
        """Create genre-based collection documents"""
        documents = []
        
        # Flatten all genres
        all_genres = []
        for genres in df['genres']:
            if isinstance(genres, list):
                all_genres.extend(genres)
        
        # Get top genres
        from collections import Counter
        genre_counts = Counter(all_genres)
        top_genres = [g for g, _ in genre_counts.most_common(5)]
        
        for genre in top_genres:
            # Filter movies by genre
            genre_movies = df[df['genres'].apply(
                lambda x: genre in x if isinstance(x, list) else False
            )].head(10)
            
            # Create document
            movie_list = []
            for idx, row in genre_movies.iterrows():
                movie_list.append(f"- **{row['title']}** ({row['release_year']}): {row['overview'][:150]}...")
            
            doc_text = f"""# {genre} Movies Collection

This collection features top-rated {genre.lower()} movies from our catalog.

## Featured {genre} Movies

{chr(10).join(movie_list)}

## Genre Characteristics
{genre} films are known for their distinct storytelling style and audience appeal.
"""
            
            metadata = {
                'title': f'{genre} Collection',
                'type': 'genre_collection',
                'genre': genre
            }
            
            documents.append({
                'content': doc_text,
                'metadata': metadata
            })
        
        return documents
    
    def save_documents(self, documents: List[Dict], filename: str = 'movie_documents.json'):
        """Save documents to JSON"""
        output_path = self.processed_path / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(documents)} documents to {output_path}")
    
    def save_as_markdown(self, documents: List[Dict]):
        """Save each document as individual markdown file"""
        md_dir = self.processed_path / 'markdown_docs'
        md_dir.mkdir(exist_ok=True)
        
        for i, doc in enumerate(documents):
            filename = f"doc_{i+1:03d}_{doc['metadata']['title'].replace(' ', '_')[:30]}.md"
            filepath = md_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(doc['content'])
        
        print(f"Saved {len(documents)} markdown files to {md_dir}")


# Main execution function
def main():
    processor = MovieDataProcessor()
    
    print("Processing Netflix data...")
    netflix_df = processor.process_netflix_data()
    print(f"Netflix movies processed: {len(netflix_df)}")
    
    print("\nProcessing TMDB data...")
    tmdb_df = processor.process_tmdb_data()
    print(f"TMDB movies processed: {len(tmdb_df)}")
    
    print("\nMerging datasets...")
    combined_df = processor.merge_datasets(netflix_df, tmdb_df)
    print(f"Combined dataset size: {len(combined_df)}")
    
    # Save combined dataset
    combined_df.to_csv('data/processed/combined_movies.csv', index=False)
    print("Saved combined dataset")
    
    print("\nCreating movie documents...")
    movie_docs = processor.create_movie_documents(combined_df, num_docs=12)
    
    print("Creating genre documents...")
    genre_docs = processor.create_genre_documents(combined_df)
    
    # Combine all documents
    all_documents = movie_docs + genre_docs
    print(f"\nTotal documents created: {len(all_documents)}")
    
    # Save documents
    processor.save_documents(all_documents)
    processor.save_as_markdown(all_documents)
    
    print("\n✅ Data processing complete!")
    print(f"Documents ready: {len(all_documents)} (minimum 10 required)")

if __name__ == "__main__":
    main()