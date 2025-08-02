#!/usr/bin/env python3
"""
State-of-the-Art Natural Language Processing for Inventory Management
"""

import re
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Configure logging with UTF-8 support for Windows
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('nlp_processing.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class CommandType(Enum):
    """Types of inventory commands"""
    ADD_QUANTITY = "add_quantity"
    SET_QUANTITY = "set_quantity"
    REDUCE_QUANTITY = "reduce_quantity"
    UPDATE_DESCRIPTION = "update_description"
    UPDATE_NOTES = "update_notes"
    SEARCH_PRODUCT = "search_product"
    GET_STATUS = "get_status"
    BULK_OPERATION = "bulk_operation"
    UNKNOWN = "unknown"

@dataclass
class ParsedCommand:
    """Structured representation of a parsed command"""
    command_type: CommandType
    product_id: Optional[str] = None
    quantity_change: Optional[float] = None
    new_quantity: Optional[float] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    search_terms: Optional[List[str]] = None
    confidence: float = 0.0
    raw_command: str = ""
    extracted_entities: Dict[str, Any] = None

class AdvancedNaturalLanguageProcessor:
    """State-of-the-art natural language processor for inventory management"""
    
    def __init__(self):
        self.product_id_patterns = [
            r'\b(\d{4}[A-Z]+\w*)\b',  # Standard format: 1015B, 1020AW
            r'\bproduct\s+([A-Z0-9]+)\b',  # "product 1015B"
            r'\bitem\s+([A-Z0-9]+)\b',  # "item 1015B"
            r'\bsku\s+([A-Z0-9]+)\b',  # "sku 1015B"
            r'\bpart\s+([A-Z0-9]+)\b',  # "part 1015B"
        ]
        
        self.quantity_patterns = [
            r'(\d+(?:\.\d+)?)\s*units?',
            r'(\d+(?:\.\d+)?)\s*pieces?',
            r'(\d+(?:\.\d+)?)\s*items?',
            r'(\d+(?:\.\d+)?)\s*qty',
            r'quantity\s*(?:of\s*)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)(?=\s*(?:to|for|units|pieces|items))',
        ]
        
        self.command_patterns = {
            CommandType.ADD_QUANTITY: [
                r'add\s+(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)?\s*to',
                r'increase\s+(?:inventory\s+)?(?:for\s+)?.*?by\s+(\d+(?:\.\d+)?)',
                r'add\s+(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)?',
                r'increment\s+.*?by\s+(\d+(?:\.\d+)?)',
                r'boost\s+.*?by\s+(\d+(?:\.\d+)?)',
            ],
            CommandType.SET_QUANTITY: [
                r'set\s+(?:quantity|qty|inventory|stock)?\s*(?:for\s+)?.*?to\s+(\d+(?:\.\d+)?)',
                r'update\s+.*?quantity\s+to\s+(\d+(?:\.\d+)?)',
                r'change\s+.*?to\s+(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)',
                r'make\s+.*?(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)',
            ],
            CommandType.REDUCE_QUANTITY: [
                r'reduce\s+.*?by\s+(\d+(?:\.\d+)?)',
                r'subtract\s+(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)?\s*from',
                r'decrease\s+.*?by\s+(\d+(?:\.\d+)?)',
                r'remove\s+(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)?',
                r'take\s+(?:away\s+)?(\d+(?:\.\d+)?)\s*(?:units?|pieces?|items?)?',
            ],
            CommandType.UPDATE_DESCRIPTION: [
                r'(?:set|update|change)\s+(?:the\s+)?description\s+(?:for\s+)?.*?to\s+(.+?)(?:\s|$)',
                r'describe\s+.*?as\s+(.+?)(?:\s|$)',
                r'rename\s+.*?to\s+(.+?)(?:\s|$)',
                r'call\s+.*?(.+?)(?:\s|$)',
                r'label\s+.*?as\s+(.+?)(?:\s|$)',
            ],
            CommandType.UPDATE_NOTES: [
                r'(?:add|set|update)\s+(?:a\s+)?note\s+(?:for\s+)?.*?(?:saying\s+)?["\']?(.+?)["\']?(?:\s|$)',
                r'note\s+(?:for\s+)?.*?[:\-]\s*(.+?)(?:\s|$)',
                r'comment\s+(?:on\s+)?.*?[:\-]\s*(.+?)(?:\s|$)',
                r'annotate\s+.*?with\s+(.+?)(?:\s|$)',
            ],
            CommandType.SEARCH_PRODUCT: [
                r'(?:find|search|look\s+for|locate)\s+(.+?)(?:\s|$)',
                r'show\s+(?:me\s+)?(.+?)(?:\s|$)',
                r'get\s+(?:info\s+(?:on|about)\s+)?(.+?)(?:\s|$)',
                r'what\s+(?:is|about)\s+(.+?)(?:\s|$)',
            ],
            CommandType.GET_STATUS: [
                r'(?:status|health|stats|statistics|info|information)',
                r'how\s+(?:is|are)\s+(?:things|everything|the\s+system)',
                r'system\s+(?:status|health|info)',
                r'what\'?s\s+(?:the\s+)?(?:status|situation)',
            ]
        }
        
        self.synonyms = {
            'add': ['increase', 'boost', 'increment', 'raise', 'up'],
            'reduce': ['decrease', 'lower', 'subtract', 'remove', 'down'],
            'set': ['change', 'update', 'make', 'adjust'],
            'units': ['pieces', 'items', 'qty', 'quantity', 'stock'],
            'product': ['item', 'sku', 'part', 'component'],
            'description': ['name', 'title', 'label', 'desc'],
        }
        
        self.context_keywords = {
            'urgency': ['urgent', 'asap', 'immediately', 'now', 'quickly', 'fast'],
            'confirmation': ['please', 'confirm', 'verify', 'check'],
            'bulk': ['all', 'bulk', 'batch', 'multiple', 'mass'],
            'location': ['warehouse', 'storage', 'shelf', 'bin', 'location'],
        }

    async def process_command(self, command: str, context: Dict[str, Any] = None) -> ParsedCommand:
        """
        Process a natural language command with advanced NLP techniques
        
        Args:
            command: Raw natural language command
            context: Additional context (user preferences, recent actions, etc.)
            
        Returns:
            ParsedCommand object with structured information
        """
        command = command.strip().lower()
        logger.info(f"Processing command: {command}")
        
        # Initialize result
        result = ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_command=command,
            extracted_entities={}
        )
        
        # Step 1: Extract product ID
        product_id = self._extract_product_id(command)
        if product_id:
            result.product_id = product_id
            result.extracted_entities['product_id'] = product_id
            logger.info(f"Extracted product ID: {product_id}")
        
        # Step 2: Determine command type and extract parameters
        command_type, confidence, extracted_data = self._classify_command(command)
        result.command_type = command_type
        result.confidence = confidence
        
        # Step 3: Extract specific parameters based on command type
        if command_type == CommandType.ADD_QUANTITY:
            result.quantity_change = extracted_data.get('quantity')
            
        elif command_type == CommandType.SET_QUANTITY:
            result.new_quantity = extracted_data.get('quantity')
            
        elif command_type == CommandType.REDUCE_QUANTITY:
            result.quantity_change = -abs(extracted_data.get('quantity', 0))
            
        elif command_type == CommandType.UPDATE_DESCRIPTION:
            result.description = extracted_data.get('description')
            
        elif command_type == CommandType.UPDATE_NOTES:
            result.notes = extracted_data.get('notes')
            
        elif command_type == CommandType.SEARCH_PRODUCT:
            result.search_terms = extracted_data.get('search_terms', [])
        
        # Step 4: Extract additional context
        result.extracted_entities.update(self._extract_context(command))
        
        # Step 5: Validate and enhance
        result = self._validate_and_enhance(result, context)
        
        logger.info(f"Processed command - Type: {result.command_type}, Confidence: {result.confidence}")
        return result

    def _extract_product_id(self, command: str) -> Optional[str]:
        """Extract product ID from command using multiple patterns"""
        for pattern in self.product_id_patterns:
            matches = re.findall(pattern, command, re.IGNORECASE)
            if matches:
                # Return the first match, prioritizing longer/more specific ones
                return max(matches, key=len).upper()
        return None

    def _classify_command(self, command: str) -> Tuple[CommandType, float, Dict[str, Any]]:
        """Classify the command type and extract relevant data"""
        best_type = CommandType.UNKNOWN
        best_confidence = 0.0
        best_data = {}
        
        for cmd_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                matches = re.search(pattern, command, re.IGNORECASE)
                if matches:
                    confidence = self._calculate_confidence(command, pattern, matches)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_type = cmd_type
                        best_data = self._extract_pattern_data(cmd_type, matches, command)
        
        return best_type, best_confidence, best_data

    def _extract_pattern_data(self, cmd_type: CommandType, matches: re.Match, command: str) -> Dict[str, Any]:
        """Extract specific data based on command type and regex matches"""
        data = {}
        
        if cmd_type in [CommandType.ADD_QUANTITY, CommandType.SET_QUANTITY, CommandType.REDUCE_QUANTITY]:
            if matches.groups():
                try:
                    data['quantity'] = float(matches.group(1))
                except (ValueError, IndexError):
                    data['quantity'] = self._extract_quantity_fallback(command)
        
        elif cmd_type == CommandType.UPDATE_DESCRIPTION:
            if matches.groups():
                description = matches.group(1).strip()
                # Clean up the description
                description = re.sub(r'^(to|as)\s+', '', description, flags=re.IGNORECASE)
                data['description'] = description
        
        elif cmd_type == CommandType.UPDATE_NOTES:
            if matches.groups():
                notes = matches.group(1).strip()
                data['notes'] = notes
        
        elif cmd_type == CommandType.SEARCH_PRODUCT:
            if matches.groups():
                search_terms = matches.group(1).strip().split()
                data['search_terms'] = search_terms
        
        return data

    def _extract_quantity_fallback(self, command: str) -> Optional[float]:
        """Fallback method to extract quantity using multiple patterns"""
        for pattern in self.quantity_patterns:
            matches = re.search(pattern, command, re.IGNORECASE)
            if matches:
                try:
                    return float(matches.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    def _calculate_confidence(self, command: str, pattern: str, matches: re.Match) -> float:
        """Calculate confidence score for a pattern match"""
        base_confidence = 0.7
        
        # Boost confidence for exact keyword matches
        keyword_boost = 0.0
        for keyword in ['add', 'set', 'update', 'increase', 'decrease']:
            if keyword in command:
                keyword_boost += 0.05
        
        # Boost confidence for having both product ID and quantity
        structure_boost = 0.0
        if self._extract_product_id(command) and self._extract_quantity_fallback(command):
            structure_boost = 0.15
        
        # Boost confidence for complete sentence structure
        completeness_boost = 0.0
        if len(command.split()) >= 4:  # Reasonable sentence length
            completeness_boost = 0.05
        
        return min(1.0, base_confidence + keyword_boost + structure_boost + completeness_boost)

    def _extract_context(self, command: str) -> Dict[str, Any]:
        """Extract contextual information from the command"""
        context = {}
        
        # Check for urgency indicators
        urgency_words = [word for word in self.context_keywords['urgency'] if word in command]
        if urgency_words:
            context['urgency'] = True
            context['urgency_indicators'] = urgency_words
        
        # Check for confirmation requests
        confirmation_words = [word for word in self.context_keywords['confirmation'] if word in command]
        if confirmation_words:
            context['requires_confirmation'] = True
        
        # Check for bulk operations
        bulk_words = [word for word in self.context_keywords['bulk'] if word in command]
        if bulk_words:
            context['bulk_operation'] = True
        
        # Extract numbers that might be relevant
        numbers = re.findall(r'\d+(?:\.\d+)?', command)
        if numbers:
            context['numbers_found'] = [float(n) for n in numbers]
        
        return context

    def _validate_and_enhance(self, result: ParsedCommand, context: Dict[str, Any] = None) -> ParsedCommand:
        """Validate and enhance the parsed command"""
        
        # Validate product ID format
        if result.product_id:
            if not re.match(r'^[A-Z0-9]+$', result.product_id):
                logger.warning(f"Unusual product ID format: {result.product_id}")
        
        # Validate quantities
        if result.quantity_change is not None:
            if abs(result.quantity_change) > 10000:
                logger.warning(f"Large quantity change detected: {result.quantity_change}")
                result.extracted_entities['large_quantity_warning'] = True
        
        if result.new_quantity is not None:
            if result.new_quantity > 50000:
                logger.warning(f"Large quantity set: {result.new_quantity}")
                result.extracted_entities['large_quantity_warning'] = True
        
        # Enhance with context
        if context:
            result.extracted_entities['user_context'] = context
        
        # Add suggestions for low confidence commands
        if result.confidence < 0.5:
            result.extracted_entities['suggestions'] = self._generate_suggestions(result.raw_command)
        
        return result

    def _generate_suggestions(self, command: str) -> List[str]:
        """Generate suggestions for unclear commands"""
        suggestions = []
        
        if any(word in command for word in ['add', 'increase', 'more']):
            suggestions.append("Try: 'Add 25 units to product 1015B'")
        
        if any(word in command for word in ['set', 'change', 'update']):
            suggestions.append("Try: 'Set quantity for 1020B to 100'")
            suggestions.append("Try: 'Update description for 1015B to Premium Steel'")
        
        if any(word in command for word in ['find', 'search', 'show']):
            suggestions.append("Try: 'Search for aluminum products'")
        
        if not suggestions:
            suggestions = [
                "Try: 'Add 50 units to product 1015B'",
                "Try: 'Set description for 1020B to Premium Metal'",
                "Try: 'Search for steel products'"
            ]
        
        return suggestions

    def generate_response_message(self, result: ParsedCommand, success: bool, details: str = "") -> str:
        """Generate a human-friendly response message"""
        if not success:
            base_msg = f"❌ Failed to process: '{result.raw_command}'"
            if result.extracted_entities.get('suggestions'):
                suggestions = result.extracted_entities['suggestions'][:2]  # Limit to 2 suggestions
                base_msg += f"\n\n💡 Try instead:\n" + "\n".join(f"• {s}" for s in suggestions)
            return base_msg
        
        # Success messages based on command type
        if result.command_type == CommandType.ADD_QUANTITY:
            return f"✅ Added {result.quantity_change} units to {result.product_id}. {details}"
        
        elif result.command_type == CommandType.SET_QUANTITY:
            return f"✅ Set quantity for {result.product_id} to {result.new_quantity} units. {details}"
        
        elif result.command_type == CommandType.REDUCE_QUANTITY:
            return f"✅ Reduced {result.product_id} by {abs(result.quantity_change)} units. {details}"
        
        elif result.command_type == CommandType.UPDATE_DESCRIPTION:
            return f"✅ Updated description for {result.product_id}. {details}"
        
        elif result.command_type == CommandType.UPDATE_NOTES:
            return f"✅ Added notes to {result.product_id}. {details}"
        
        else:
            return f"✅ Processed command successfully. {details}"

# Example usage and testing
async def test_nlp_processor():
    """Test the NLP processor with various commands"""
    processor = AdvancedNaturalLanguageProcessor()
    
    test_commands = [
        "Add 50 units to product 1015B",
        "Set the quantity for item 1020B to 200 pieces",
        "Increase inventory for 1025AW by 100 units",
        "Update the description for product 1015B to Premium Steel Grade A",
        "Reduce 1020B by 25 units",
        "Search for aluminum products",
        "What's the status of the system?",
        "Please add a note to 1015B saying urgent reorder needed",
        "Make product 1030C have 500 units",
        "Find all steel items",
    ]
    
    print("🧪 Testing Advanced Natural Language Processor")
    print("=" * 60)
    
    for command in test_commands:
        print(f"\n📝 Command: '{command}'")
        result = await processor.process_command(command)
        
        print(f"   Type: {result.command_type.value}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Product ID: {result.product_id}")
        
        if result.quantity_change:
            print(f"   Quantity Change: {result.quantity_change}")
        if result.new_quantity:
            print(f"   New Quantity: {result.new_quantity}")
        if result.description:
            print(f"   Description: {result.description}")
        if result.notes:
            print(f"   Notes: {result.notes}")
        if result.search_terms:
            print(f"   Search Terms: {result.search_terms}")
        
        # Generate response message
        response = processor.generate_response_message(result, True, "Test successful")
        print(f"   Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_nlp_processor())