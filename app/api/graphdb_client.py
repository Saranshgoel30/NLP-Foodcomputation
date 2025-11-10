"""
GraphDB Client with httpx
Handles SPARQL queries with authentication, timeouts, and retry logic
"""
import httpx
from typing import List, Dict, Any, Optional
import structlog
from config import Settings
from models import Recipe

logger = structlog.get_logger()


class GraphDBClient:
    """Client for querying MMFOOD GraphDB via SPARQL endpoint"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.endpoint = settings.graphdb_endpoint
        self.timeout = settings.graphdb_timeout
        self.named_graph = settings.graphdb_named_graph
        
        # Setup authentication if provided
        self.auth = None
        if settings.graphdb_username and settings.graphdb_password:
            self.auth = httpx.BasicAuth(
                settings.graphdb_username,
                settings.graphdb_password
            )
        
        # Create reusable client with timeout and retry
        self.client = httpx.Client(
            timeout=self.timeout,
            auth=self.auth,
            follow_redirects=True
        )
        
        logger.info(
            "graphdb_client_initialized",
            endpoint=self.endpoint,
            timeout=self.timeout
        )
    
    def execute_sparql(
        self,
        query: str,
        accept: str = "application/sparql-results+json"
    ) -> Dict[str, Any]:
        """
        Execute SPARQL query against GraphDB
        
        Args:
            query: SPARQL query string
            accept: Response format (default JSON)
            
        Returns:
            Parsed JSON response from GraphDB
            
        Raises:
            httpx.HTTPError: On request failure
        """
        headers = {
            "Accept": accept,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {"query": query}
        
        try:
            logger.debug(
                "executing_sparql",
                query_length=len(query),
                endpoint=self.endpoint
            )
            
            response = self.client.post(
                self.endpoint,
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            
            logger.info(
                "sparql_executed",
                bindings_count=len(result.get("results", {}).get("bindings", [])),
                duration_ms=response.elapsed.total_seconds() * 1000
            )
            
            return result
            
        except httpx.HTTPError as e:
            logger.error(
                "sparql_execution_failed",
                error=str(e),
                query_preview=query[:200]
            )
            raise
    
    def parse_bindings_to_recipes(self, bindings: List[Dict[str, Any]]) -> List[Recipe]:
        """
        Parse SPARQL bindings to Recipe objects
        
        Args:
            bindings: List of SPARQL result bindings
            
        Returns:
            List of Recipe objects
        """
        recipes = []
        
        for binding in bindings:
            try:
                # Extract IRI (required)
                iri = binding.get("recipe", {}).get("value")
                if not iri:
                    continue
                
                # Parse ingredients (pipe-separated in GROUP_CONCAT)
                ingredients_str = binding.get("ingredients", {}).get("value", "")
                ingredients = [
                    ing.strip() 
                    for ing in ingredients_str.split("|") 
                    if ing.strip()
                ] if ingredients_str else None
                
                # Build Recipe object
                recipe = Recipe(
                    iri=iri,
                    title=binding.get("title", {}).get("value"),
                    url=binding.get("url", {}).get("value"),
                    course=binding.get("course", {}).get("value"),
                    cuisine=binding.get("cuisine", {}).get("value"),
                    diet=binding.get("diet", {}).get("value"),
                    servings=binding.get("servings", {}).get("value"),
                    ingredients=ingredients,
                    instructions=binding.get("instructions", {}).get("value"),
                    difficulty=binding.get("difficulty", {}).get("value"),
                    cookTime=binding.get("cookTime", {}).get("value"),
                    totalTime=binding.get("totalTime", {}).get("value")
                )
                
                recipes.append(recipe)
                
            except Exception as e:
                logger.warning(
                    "failed_to_parse_recipe",
                    error=str(e),
                    binding_keys=list(binding.keys())
                )
                continue
        
        return recipes
    
    def search_recipes(self, sparql_query: str) -> List[Recipe]:
        """
        Execute SPARQL query and return parsed Recipe objects
        
        Args:
            sparql_query: Complete SPARQL query string
            
        Returns:
            List of Recipe objects
        """
        result = self.execute_sparql(sparql_query)
        bindings = result.get("results", {}).get("bindings", [])
        return self.parse_bindings_to_recipes(bindings)
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
        logger.info("graphdb_client_closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
