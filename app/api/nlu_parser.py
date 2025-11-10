"""
NLU Parser - Extract structured constraints from natural language queries
Uses rule-based extraction with patterns for Indian food queries
"""
import re
from typing import List, Tuple, Optional
import structlog
from .models import QueryConstraints, Language

logger = structlog.get_logger()


# Exclusion patterns
EXCLUSION_PATTERNS = [
    r'without\s+(\w+(?:\s+\w+)?)',
    r'no\s+(\w+(?:\s+\w+)?)',
    r'except\s+(\w+(?:\s+\w+)?)',
    r'excluding\s+(\w+(?:\s+\w+)?)',
    r'not\s+(\w+(?:\s+\w+)?)',
    r'minus\s+(\w+(?:\s+\w+)?)',
]

# Time patterns
TIME_PATTERNS = [
    r'(?:under|less than|below|<=|<)\s*(\d+)\s*(?:min|minute|minutes)',
    r'(?:within|in)\s*(\d+)\s*(?:min|minute|minutes)',
    r'(\d+)\s*(?:min|minute|minutes)\s*or\s*less',
    r'max\s*(\d+)\s*(?:min|minute|minutes)',
]

# Cuisine keywords
CUISINES = [
    'indian', 'chinese', 'italian', 'mexican', 'thai', 'japanese',
    'american', 'french', 'mediterranean', 'korean', 'vietnamese',
    'bengali', 'punjabi', 'south indian', 'north indian', 'gujarati',
    'maharashtrian', 'rajasthani', 'goan', 'kashmiri', 'hyderabadi'
]

# Diet keywords
DIETS = [
    'vegan', 'vegetarian', 'non-vegetarian', 'jain', 'halal', 'kosher',
    'gluten-free', 'dairy-free', 'nut-free', 'egg-free', 'lactose-free'
]

# Course keywords
COURSES = [
    'breakfast', 'lunch', 'dinner', 'snack', 'appetizer', 'starter',
    'main course', 'dessert', 'beverage', 'side dish', 'salad'
]

# Technique/keyword patterns
TECHNIQUE_KEYWORDS = [
    'dum cook', 'tandoor', 'tadka', 'tempering', 'roast', 'grill',
    'steam', 'bake', 'fry', 'deep fry', 'stir fry', 'pressure cook',
    'slow cook', 'marinate'
]

# Common ingredient stopwords to filter out
STOPWORDS = {
    'a', 'an', 'the', 'with', 'and', 'or', 'for', 'of', 'in', 'to',
    'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'recipe', 'recipes', 'dish', 'dishes', 'food', 'meal'
}


def extract_exclusions(text: str) -> List[str]:
    """Extract excluded ingredients from text"""
    exclusions = []
    text_lower = text.lower()
    
    for pattern in EXCLUSION_PATTERNS:
        matches = re.finditer(pattern, text_lower, re.IGNORECASE)
        for match in matches:
            ingredient = match.group(1).strip()
            if ingredient and ingredient not in STOPWORDS:
                exclusions.append(ingredient)
                logger.debug("extracted_exclusion", ingredient=ingredient, pattern=pattern)
    
    return list(set(exclusions))  # Remove duplicates


def extract_time_constraints(text: str) -> Tuple[Optional[int], Optional[int]]:
    """
    Extract time constraints from text
    Returns (max_cook_minutes, max_total_minutes)
    """
    text_lower = text.lower()
    max_cook = None
    max_total = None
    
    # Check for cooking time specific
    if 'cook time' in text_lower or 'cooking time' in text_lower:
        for pattern in TIME_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                max_cook = int(match.group(1))
                logger.debug("extracted_cook_time", minutes=max_cook)
                break
    
    # Check for total time specific
    if 'total time' in text_lower:
        for pattern in TIME_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                max_total = int(match.group(1))
                logger.debug("extracted_total_time", minutes=max_total)
                break
    
    # If no specific type, use as cook time
    if not max_cook and not max_total:
        for pattern in TIME_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                max_cook = int(match.group(1))
                logger.debug("extracted_time_default", minutes=max_cook)
                break
    
    return max_cook, max_total


def extract_cuisines(text: str) -> List[str]:
    """Extract cuisine types from text"""
    text_lower = text.lower()
    found_cuisines = []
    
    # Sort by length (longest first) to match multi-word cuisines first
    sorted_cuisines = sorted(CUISINES, key=len, reverse=True)
    
    for cuisine in sorted_cuisines:
        if cuisine in text_lower:
            found_cuisines.append(cuisine.title())
            logger.debug("extracted_cuisine", cuisine=cuisine)
    
    return found_cuisines


def extract_diets(text: str) -> List[str]:
    """Extract dietary restrictions from text"""
    text_lower = text.lower()
    found_diets = []
    
    for diet in DIETS:
        if diet in text_lower:
            found_diets.append(diet.title())
            logger.debug("extracted_diet", diet=diet)
    
    return found_diets


def extract_courses(text: str) -> List[str]:
    """Extract course types from text"""
    text_lower = text.lower()
    found_courses = []
    
    # Sort by length (longest first) to match multi-word courses first
    sorted_courses = sorted(COURSES, key=len, reverse=True)
    
    for course in sorted_courses:
        if course in text_lower:
            found_courses.append(course.title())
            logger.debug("extracted_course", course=course)
    
    return found_courses


def extract_keywords(text: str) -> List[str]:
    """Extract technique keywords from text"""
    text_lower = text.lower()
    found_keywords = []
    
    for keyword in TECHNIQUE_KEYWORDS:
        if keyword in text_lower:
            found_keywords.append(keyword)
            logger.debug("extracted_keyword", keyword=keyword)
    
    return found_keywords


def extract_includes(text: str, exclusions: List[str]) -> List[str]:
    """
    Extract included ingredients from text
    This is the trickiest part - we look for food-related nouns
    that aren't in exclusions or stopwords
    """
    text_lower = text.lower()
    
    # Remove exclusion phrases first
    for pattern in EXCLUSION_PATTERNS:
        text_lower = re.sub(pattern, '', text_lower)
    
    # Remove time phrases
    for pattern in TIME_PATTERNS:
        text_lower = re.sub(pattern, '', text_lower)
    
    # Remove cuisines, diets, courses from consideration
    for cuisine in CUISINES:
        text_lower = text_lower.replace(cuisine, '')
    for diet in DIETS:
        text_lower = text_lower.replace(diet, '')
    for course in COURSES:
        text_lower = text_lower.replace(course, '')
    
    # Extract potential ingredient words
    # Look for sequences of 1-2 words
    words = re.findall(r'\b[a-z]+(?:\s+[a-z]+)?\b', text_lower)
    
    includes = []
    for word in words:
        word = word.strip()
        # Filter out stopwords, exclusions, and very short words
        if (word and 
            len(word) > 2 and 
            word not in STOPWORDS and 
            word not in [e.lower() for e in exclusions] and
            not word.isdigit()):
            includes.append(word)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_includes = []
    for item in includes:
        if item not in seen:
            seen.add(item)
            unique_includes.append(item)
    
    logger.debug("extracted_includes", count=len(unique_includes), items=unique_includes)
    return unique_includes


def calculate_confidence(constraints: QueryConstraints, text: str) -> float:
    """
    Calculate confidence score based on how well we parsed the query
    Higher confidence when we extract multiple structured constraints
    """
    score = 0.5  # Base confidence
    
    # Boost for each type of constraint found
    if constraints.include:
        score += 0.1
    if constraints.exclude:
        score += 0.15  # Exclusions are more important
    if constraints.cuisine:
        score += 0.1
    if constraints.diet:
        score += 0.1
    if constraints.course:
        score += 0.05
    if constraints.maxCookMinutes or constraints.maxTotalMinutes:
        score += 0.1
    if constraints.keywords:
        score += 0.05
    
    # Cap at 1.0
    return min(score, 1.0)


def parse_query(text: str, lang: Language = 'en') -> Tuple[QueryConstraints, float]:
    """
    Main NLU parsing function
    
    Args:
        text: Natural language query
        lang: Source language (for future expansion)
        
    Returns:
        (QueryConstraints, confidence_score)
    """
    logger.info("parsing_query", text=text, lang=lang)
    
    # Extract all constraint types
    exclusions = extract_exclusions(text)
    max_cook, max_total = extract_time_constraints(text)
    cuisines = extract_cuisines(text)
    diets = extract_diets(text)
    courses = extract_courses(text)
    keywords = extract_keywords(text)
    
    # Extract includes last (after removing other elements)
    includes = extract_includes(text, exclusions)
    
    # Build constraints object
    constraints = QueryConstraints(
        include=includes if includes else None,
        exclude=exclusions if exclusions else None,
        cuisine=cuisines if cuisines else None,
        diet=diets if diets else None,
        maxCookMinutes=max_cook,
        maxTotalMinutes=max_total,
        course=courses if courses else None,
        keywords=keywords if keywords else None
    )
    
    confidence = calculate_confidence(constraints, text)
    
    logger.info(
        "parsed_query",
        constraints=constraints.model_dump(exclude_none=True),
        confidence=confidence
    )
    
    return constraints, confidence
