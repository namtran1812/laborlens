import type {
  MetadataRoute,
} from "next";

export default function sitemap(): MetadataRoute.Sitemap {
  const base =
    "https://laborlens-eosin.vercel.app";

  return [
    {
      url: `${base}/`,
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${base}/replay`,
      changeFrequency: "monthly",
      priority: 0.9,
    },
    {
      url: `${base}/episodes/2024-06-01`,
      changeFrequency: "monthly",
      priority: 0.8,
    },
    {
      url: `${base}/methodology`,
      changeFrequency: "monthly",
      priority: 0.7,
    },
  ];
}
