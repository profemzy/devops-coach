"""Web search service for up-to-date information retrieval."""

import os
from typing import Any, Dict, List, Optional

from tavily import TavilyClient

from config import settings


class WebSearchService:
    """Service for web search using Tavily API."""

    def __init__(self):
        """Initialize the web search service."""
        self.api_key = settings.TAVILY_API_KEY or os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search(
        self,
        query: str,
        max_results: int = 10,
        search_depth: str = "basic",
        include_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Perform a web search using Tavily.

        :param query: Search query string
        :param max_results: Maximum number of results to return
        :param search_depth: "basic" or "advanced" search
        :param include_domains: Optional list of domains to limit search to
        :return: Search results dictionary
        """
        if self.client is None:
            return {"error": "Tavily API key not configured"}

        try:
            kwargs = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
            }

            if include_domains:
                kwargs["include_domains"] = include_domains

            return self.client.search(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    def search_devops_resources(
        self, topic: str, max_results: int = 5
    ) -> List[Dict[str, str]]:
        """
        Search for DevOps learning resources on specific topics.

        :param topic: The DevOps topic to search for
        :param max_results: Maximum number of results
        :return: List of formatted resource results
        """
        # Search reputable DevOps learning resources
        query = f"DevOps {topic} tutorial best practices 2024 2025"
        result = self.search(
            query,
            max_results=max_results,
            include_domains=[
                "linuxfoundation.org",
                "kubebyexample.com",
                "docker.com",
                "kubernetes.io",
                "aws.amazon.com",
                "learn.microsoft.com",
                "redhat.com",
                "canonical.com",
                "github.com",
                "terraform.io",
                "jenkins.io",
                "prometheus.io",
                "grafana.com",
                "istio.io",
                "envoyproxy.io",
            ],
        )

        if "error" in result:
            return []

        # Format results
        formatted = []
        for item in result.get("results", []):
            formatted.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:200],
                }
            )
        return formatted

    def get_latest_certification_info(
        self, certification: str
    ) -> Dict[str, Any]:
        """
        Get latest information about a specific DevOps certification.

        :param certification: Name of the certification (e.g., "CKA", "AWS DevOps")
        :return: Dictionary with certification info
        """
        query = (
            f"{certification} certification 2024 2025 requirements exam cost"
        )
        result = self.search(query, max_results=5, search_depth="advanced")

        if "error" in result:
            return {"error": result["error"]}

        return {
            "certification": certification,
            "results": result.get("results", []),
            "answer": result.get("answer", ""),
        }

    def get_current_devops_trends(self) -> List[Dict[str, str]]:
        """
        Get current DevOps trends and technologies.

        :return: List of trending topics and resources
        """
        query = "DevOps trends 2025 best practices new technologies"
        result = self.search(query, max_results=8, search_depth="advanced")

        if "error" in result:
            return []

        formatted = []
        for item in result.get("results", []):
            formatted.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:200],
                }
            )
        return formatted


# Singleton instance
_web_search_service = None


def get_web_search_service() -> WebSearchService:
    """Get or create the web search service singleton."""
    global _web_search_service
    if _web_search_service is None:
        _web_search_service = WebSearchService()
    return _web_search_service
