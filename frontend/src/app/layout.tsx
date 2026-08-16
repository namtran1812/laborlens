import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
} from "next/font/google";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    "https://laborlens-eosin.vercel.app",
  ),
  title: {
    default:
      "LaborLens — Point-in-Time Labor-Market Intelligence",
    template: "%s | LaborLens",
  },
  description:
    "Revision-aware labor-market research using FRED/ALFRED vintages, point-in-time reconstruction, release-aware replay, evidence validation, and grounded AI explanations.",
  applicationName: "LaborLens",
  keywords: [
    "labor market",
    "economic research",
    "FRED",
    "ALFRED",
    "point-in-time data",
    "economic revisions",
    "FastAPI",
    "ClickHouse",
    "grounded AI",
  ],
  authors: [
    {
      name: "Nam Tran",
    },
  ],
  creator: "Nam Tran",
  openGraph: {
    type: "website",
    url: "/",
    title:
      "LaborLens — Point-in-Time Labor-Market Intelligence",
    description:
      "Reconstruct what economic data actually showed at historical information dates and measure how conclusions changed after revisions.",
    siteName: "LaborLens",
  },
  twitter: {
    card: "summary_large_image",
    title:
      "LaborLens — Point-in-Time Labor-Market Intelligence",
    description:
      "Revision-aware economic research with release replay and grounded AI interpretation.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        {children}
      </body>
    </html>
  );
}
