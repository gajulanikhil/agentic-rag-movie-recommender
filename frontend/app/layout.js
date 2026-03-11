import { Rajdhani } from "next/font/google";
import "./globals.css";

const rajdhani = Rajdhani({
  subsets: ["latin"],
  weight: ['400', '500', '600', '700'],
  variable: '--font-rajdhani'
});

export const metadata = {
  title: "AI Movie Recommender",
  description: "Futuristic AI Movie Recommender Interface",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={rajdhani.className}>
        {children}
      </body>
    </html>
  );
}
