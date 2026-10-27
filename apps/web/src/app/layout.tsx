import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export const metadata = { title: "AIVideoStudio", description: "AI-directed video production" };

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="top">
          <Link className="brand" href="/">AIVideoStudio</Link>
          <nav aria-label="Main"><Link href="/projects/new">New project</Link></nav>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
