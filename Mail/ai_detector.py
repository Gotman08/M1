"""
AI-based email threat detection using local machine learning models.
"""

import logging
import re
from typing import Tuple, Optional, Dict
import numpy as np

logger = logging.getLogger(__name__)

# Try to import ML libraries
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers not available, AI detection disabled")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available, fallback AI disabled")


class AIEmailDetector:
    """AI-based phishing and malware detection."""
    
    def __init__(self, use_transformer: bool = True, model_name: str = None):
        """
        Initialize AI detector.
        
        @param use_transformer Use transformer model if available
        @param model_name Custom model name (default: distilbert phishing detector)
        """
        self.transformer_model = None
        self.fallback_model = None
        self.vectorizer = None
        self.use_transformer = use_transformer and TRANSFORMERS_AVAILABLE
        
        if self.use_transformer:
            self._load_transformer_model(model_name)
        elif SKLEARN_AVAILABLE:
            self._initialize_fallback_model()
    
    def _load_transformer_model(self, model_name: Optional[str]):
        """
        Load transformer model for phishing detection.
        
        @param model_name Model name or path
        """
        try:
            # Use lightweight model for fast inference
            default_model = "distilbert-base-uncased"
            model_to_use = model_name or default_model
            
            logger.info(f"loading transformer model: {model_to_use}")
            
            # Load zero-shot classification pipeline
            self.transformer_model = pipeline(
                "text-classification",
                model=model_to_use,
                device=-1,  # CPU
                max_length=512,
                truncation=True
            )
            
            logger.info("transformer model loaded successfully")
        
        except Exception as e:
            logger.error(f"failed to load transformer model: {e}")
            self.use_transformer = False
            if SKLEARN_AVAILABLE:
                self._initialize_fallback_model()
    
    def _initialize_fallback_model(self):
        """Initialize rule-based + TF-IDF fallback model."""
        try:
            logger.info("initializing fallback ai model")
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=500,
                ngram_range=(1, 3),
                stop_words='english'
            )
            
            # Train on synthetic phishing patterns
            training_data = self._get_synthetic_training_data()
            X_train = self.vectorizer.fit_transform(training_data['texts'])
            y_train = training_data['labels']
            
            # Train Random Forest
            self.fallback_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.fallback_model.fit(X_train, y_train)
            
            logger.info("fallback model initialized")
        
        except Exception as e:
            logger.error(f"fallback model init failed: {e}")
    
    def _get_synthetic_training_data(self) -> Dict:
        """
        Generate synthetic training data for fallback model.
        
        @return Dict with texts and labels
        """
        phishing_patterns = [
            "urgent verify your account immediately",
            "click here to claim your prize now",
            "your account has been suspended confirm identity",
            "update payment information to avoid suspension",
            "you have won lottery inheritance claim now",
            "reset your password unusual activity detected",
            "confirm credit card details security alert",
            "limited time offer act now or lose access",
            "wire transfer required immediate action needed",
            "tax refund available click link to receive",
            "package delivery failed update address now",
            "invoice attached please pay immediately",
            "your social security number has been compromised",
            "bitcoin investment opportunity guaranteed returns",
            "bank account locked verify identity urgently"
        ] * 10  # Repeat for better training
        
        legitimate_patterns = [
            "thank you for your order confirmation",
            "meeting scheduled for tomorrow at 3pm",
            "quarterly report attached for review",
            "team lunch next friday please rsvp",
            "project update and next steps discussion",
            "welcome to our newsletter subscription",
            "invoice for services rendered last month",
            "appointment reminder for next week",
            "feedback requested on recent proposal",
            "monthly summary of account activity",
            "document shared for collaboration",
            "event invitation please save the date",
            "password changed successfully notification",
            "receipt for your recent purchase",
            "system maintenance scheduled notification"
        ] * 10
        
        texts = phishing_patterns + legitimate_patterns
        labels = [1] * len(phishing_patterns) + [0] * len(legitimate_patterns)
        
        return {'texts': texts, 'labels': labels}
    
    def analyze_with_transformer(self, text: str) -> Tuple[float, str]:
        """
        Analyze email with transformer model.
        
        @param text Email text
        @return Tuple (confidence_score, prediction)
        """
        if not self.transformer_model:
            return 0.0, "model unavailable"
        
        try:
            # Truncate very long texts
            text_truncated = text[:2000]
            
            # Run inference
            result = self.transformer_model(text_truncated)[0]
            
            label = result['label'].lower()
            score = result['score']
            
            # Map generic labels to phishing detection
            # Negative sentiment or suspicious patterns indicate phishing
            if 'negative' in label or 'spam' in label or 'phishing' in label:
                confidence = score
                prediction = "phishing"
            elif 'positive' in label or 'ham' in label or 'legitimate' in label:
                confidence = 1.0 - score
                prediction = "legitimate"
            else:
                # Neutral - use heuristic
                confidence = 0.5
                prediction = "unknown"
            
            logger.debug(f"transformer result: {prediction} ({confidence:.2f})")
            return confidence, prediction
        
        except Exception as e:
            logger.error(f"transformer analysis failed: {e}")
            return 0.0, "error"
    
    def analyze_with_fallback(self, text: str) -> Tuple[float, str]:
        """
        Analyze email with fallback ML model.
        
        @param text Email text
        @return Tuple (confidence_score, prediction)
        """
        if not self.fallback_model or not self.vectorizer:
            return 0.0, "model unavailable"
        
        try:
            # Vectorize text
            X = self.vectorizer.transform([text])
            
            # Predict
            prediction = self.fallback_model.predict(X)[0]
            probabilities = self.fallback_model.predict_proba(X)[0]
            
            if prediction == 1:
                confidence = probabilities[1]
                result = "phishing"
            else:
                confidence = probabilities[0]
                result = "legitimate"
            
            logger.debug(f"fallback result: {result} ({confidence:.2f})")
            return confidence, result
        
        except Exception as e:
            logger.error(f"fallback analysis failed: {e}")
            return 0.0, "error"
    
    def analyze_semantic_features(self, subject: str, body: str) -> Dict:
        """
        Extract semantic features for analysis.
        
        @param subject Email subject
        @param body Email body
        @return Dict with semantic features
        """
        features = {
            'urgency_level': 0,
            'emotional_manipulation': 0,
            'authority_impersonation': 0,
            'financial_pressure': 0,
            'scarcity_tactics': 0
        }
        
        text = (subject + " " + body).lower()
        
        # Urgency indicators
        urgency_words = ['urgent', 'immediately', 'asap', 'now', 'quick', 'hurry', 'expire']
        features['urgency_level'] = sum(1 for word in urgency_words if word in text)
        
        # Emotional manipulation
        emotional_words = ['worried', 'concerned', 'afraid', 'shocked', 'surprised', 'congratulations']
        features['emotional_manipulation'] = sum(1 for word in emotional_words if word in text)
        
        # Authority impersonation
        authority_words = ['ceo', 'manager', 'director', 'irs', 'police', 'government', 'bank']
        features['authority_impersonation'] = sum(1 for word in authority_words if word in text)
        
        # Financial pressure
        financial_words = ['payment', 'invoice', 'debt', 'owe', 'refund', 'tax', 'credit card']
        features['financial_pressure'] = sum(1 for word in financial_words if word in text)
        
        # Scarcity tactics
        scarcity_words = ['limited', 'only', 'last chance', 'exclusive', 'rare', 'once']
        features['scarcity_tactics'] = sum(1 for word in scarcity_words if word in text)
        
        return features
    
    def calculate_ai_threat_score(self, subject: str, body: str, 
                                  html_body: Optional[str] = None) -> Tuple[int, Dict]:
        """
        Calculate AI-based threat score.
        
        @param subject Email subject
        @param body Email body text
        @param html_body HTML body (optional)
        @return Tuple (threat_score, details)
        """
        score = 0
        details = {
            'ai_prediction': 'unknown',
            'ai_confidence': 0.0,
            'semantic_features': {},
            'model_used': 'none'
        }
        
        # Prepare text for analysis
        full_text = f"{subject}\n\n{body}"
        if len(full_text) < 20:
            return 0, details
        
        # Run AI analysis
        if self.use_transformer and self.transformer_model:
            confidence, prediction = self.analyze_with_transformer(full_text)
            details['model_used'] = 'transformer'
            details['ai_prediction'] = prediction
            details['ai_confidence'] = confidence
            
            if prediction == "phishing" and confidence > 0.7:
                score += int(confidence * 50)  # Max 50 points
        
        elif self.fallback_model:
            confidence, prediction = self.analyze_with_fallback(full_text)
            details['model_used'] = 'fallback'
            details['ai_prediction'] = prediction
            details['ai_confidence'] = confidence
            
            if prediction == "phishing" and confidence > 0.6:
                score += int(confidence * 40)  # Max 40 points
        
        # Semantic feature analysis
        semantic = self.analyze_semantic_features(subject, body)
        details['semantic_features'] = semantic
        
        # Add semantic scores
        if semantic['urgency_level'] >= 3:
            score += 15
        if semantic['emotional_manipulation'] >= 2:
            score += 10
        if semantic['authority_impersonation'] >= 2:
            score += 15
        if semantic['financial_pressure'] >= 2:
            score += 10
        if semantic['scarcity_tactics'] >= 2:
            score += 10
        
        logger.info(f"ai analysis: score={score}, prediction={details['ai_prediction']}, "
                   f"confidence={details['ai_confidence']:.2f}")
        
        return score, details
    
    def is_available(self) -> bool:
        """
        Check if AI detection is available.
        
        @return True if any model is loaded
        """
        return (self.transformer_model is not None or 
                self.fallback_model is not None)
