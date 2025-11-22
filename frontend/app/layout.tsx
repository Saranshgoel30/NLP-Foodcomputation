import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Food Intelligence Platform",
  description: "AI-powered semantic recipe search",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
