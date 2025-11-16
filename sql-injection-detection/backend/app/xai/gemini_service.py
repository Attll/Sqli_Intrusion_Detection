import google.generativeai as genai
from typing import Dict, Any
from app.config import settings
import json

class GeminiExplainer:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    def generate_explanation(
        self,
        query: str,
        is_malicious: bool,
        confidence: float,
        xai_output: Dict[str, Any],
        style: str = 'simple'
    ) -> str:
        """
        Generate natural language explanation using Gemini
        
        Args:
            query: The SQL query
            is_malicious: Detection result
            confidence: Confidence score
            xai_output: XAI explanation output
            style: 'simple', 'technical', or 'detailed'
        
        Returns:
            Natural language explanation
        """
        
        # Prepare prompt based on style
        if style == 'simple':
            prompt = self._create_simple_prompt(query, is_malicious, confidence, xai_output)
        elif style == 'technical':
            prompt = self._create_technical_prompt(query, is_malicious, confidence, xai_output)
        else:  # detailed
            prompt = self._create_detailed_prompt(query, is_malicious, confidence, xai_output)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fallback to template-based explanation
            return self._fallback_explanation(query, is_malicious, confidence, xai_output, style)
    
    def _create_simple_prompt(self, query: str, is_malicious: bool, confidence: float, xai_output: Dict) -> str:
        top_features = xai_output.get('top_features', [])[:5]
        
        prompt = f"""
You are a cybersecurity assistant explaining SQL injection detection results to non-technical users.

Query analyzed: "{query}"

Detection Result: {"🚨 BLOCKED - Potential SQL Injection Attack" if is_malicious else "✅ ALLOWED - Safe Query"}
Confidence: {confidence*100:.1f}%

Key factors in this decision:
{self._format_features_simple(top_features)}

Explain in 2-3 simple sentences why this query was {("blocked" if is_malicious else "allowed")}. 
Use simple language, avoid jargon, and be reassuring but clear.
"""
        return prompt
    
    def _create_technical_prompt(self, query: str, is_malicious: bool, confidence: float, xai_output: Dict) -> str:
        top_features = xai_output.get('top_features', [])[:10]
        
        prompt = f"""
You are a cybersecurity expert providing technical analysis of SQL injection detection.

Query: "{query}"

Detection: {"Malicious" if is_malicious else "Benign"}
Confidence: {confidence*100:.2f}%
XAI Method: {xai_output.get('method', 'Unknown')}

Top Features:
{self._format_features_technical(top_features)}

Provide a technical explanation (3-4 sentences) covering:
1. Primary attack indicators or safety indicators
2. Feature analysis
3. Confidence interpretation
"""
        return prompt
    
    def _create_detailed_prompt(self, query: str, is_malicious: bool, confidence: float, xai_output: Dict) -> str:
        top_features = xai_output.get('top_features', [])[:10]
        
        prompt = f"""
You are a cybersecurity analyst providing comprehensive SQL injection analysis.

Query Under Analysis: "{query}"

Detection Result: {"SQL Injection Attack Detected" if is_malicious else "Safe Query - No Threat Detected"}
Confidence Level: {confidence*100:.2f}%
Explainability Method: {xai_output.get('method', 'Unknown')}

Feature Analysis:
{self._format_features_detailed(top_features)}

Provide a detailed explanation including:
1. Executive Summary (1 sentence)
2. Technical Analysis (what patterns were detected)
3. Risk Assessment
4. Recommendations
5. Educational note about the specific technique (if applicable)

Format with clear sections. Be thorough but concise.
"""
        return prompt
    
    def _format_features_simple(self, features: list) -> str:
        if not features:
            return "- No specific features highlighted"
        
        lines = []
        for f in features[:3]:
            feat_name = f.get('feature', 'unknown')
            # Simplify feature names
            if feat_name.startswith('tfidf_'):
                feat_name = 'text pattern'
            lines.append(f"- {feat_name}")
        return '\n'.join(lines)
    
    def _format_features_technical(self, features: list) -> str:
        if not features:
            return "- No features available"
        
        lines = []
        for f in features:
            feat_name = f.get('feature', 'unknown')
            importance = f.get('importance', 0)
            impact = f.get('impact', 'unknown')
            lines.append(f"- {feat_name}: {importance:.4f} ({impact})")
        return '\n'.join(lines)
    
    def _format_features_detailed(self, features: list) -> str:
        if not features:
            return "No features analyzed"
        
        lines = []
        for i, f in enumerate(features, 1):
            feat_name = f.get('feature', 'unknown')
            importance = f.get('importance', 0)
            impact = f.get('impact', 'unknown')
            lines.append(f"{i}. {feat_name}")
            lines.append(f"   Importance: {importance:.4f}")
            lines.append(f"   Impact: {impact}")
        return '\n'.join(lines)
    
    def _fallback_explanation(
        self,
        query: str,
        is_malicious: bool,
        confidence: float,
        xai_output: Dict,
        style: str
    ) -> str:
        """Fallback explanation when Gemini API fails"""
        
        if style == 'simple':
            if is_malicious:
                return f"This query was blocked because it shows patterns commonly used in SQL injection attacks (confidence: {confidence*100:.1f}%). The system detected suspicious keywords and structures that could manipulate your database."
            else:
                return f"This query appears safe and was allowed (confidence: {confidence*100:.1f}%). It doesn't contain patterns associated with SQL injection attacks."
        
        elif style == 'technical':
            top_features = xai_output.get('top_features', [])[:5]
            features_str = ', '.join([f['feature'] for f in top_features])
            
            if is_malicious:
                return f"SQL injection detected with {confidence*100:.2f}% confidence. Key indicators: {features_str}. The query contains patterns matching known attack vectors."
            else:
                return f"Query classified as benign with {confidence*100:.2f}% confidence. Analysis of features ({features_str}) indicates normal SQL syntax without injection patterns."
        
        else:  # detailed
            top_features = xai_output.get('top_features', [])[:5]
            
            if is_malicious:
                explanation = f"""
**THREAT DETECTED**

**Summary:** SQL injection attack identified with {confidence*100:.2f}% confidence.

**Technical Analysis:**
The query contains multiple indicators of SQL injection attempts:
"""
                for f in top_features:
                    explanation += f"\n- {f.get('feature', 'N/A')}: Impact score {f.get('importance', 0):.3f}"
                
                explanation += "\n\n**Risk:** HIGH - This query could potentially compromise database security."
                explanation += "\n\n**Action:** Query has been blocked to protect your system."
                
                return explanation
            else:
                return f"""
**QUERY APPROVED**

**Summary:** Query analyzed and deemed safe with {confidence*100:.2f}% confidence.

**Analysis:** The query structure and content match normal SQL patterns without injection indicators.

**Risk:** LOW - No security concerns identified.

**Action:** Query allowed to proceed.
"""
