import re
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class HarassmentDetector:
    """
    Hybrid harassment detection system combining rule-based and ML approaches.
    Prioritizes harmful intent, bad words, threats, sexual content, and repetition.
    """
    
    def __init__(self):
        # Load or create ML model
        self.model = self._load_or_create_model()
        
        # Keywords organized by category and severity
        self.keywords = {
            'sexual': {
                'high': ['rape', 'molest', 'grope', 'assault sexually', 'sexual assault', 
                        'touched me inappropriately', 'forced me to', 'sex without consent'],
                'medium': ['sexual', 'nude', 'naked', 'body parts', 'penis', 'vagina', 'breast',
                          'sexual advances', 'sexual favor', 'sleep with', 'sexting'],
                'low': ['flirt', 'attractive', 'sexy', 'hot', 'beautiful']
            },
            'threat': {
                'high': ['kill you', 'hurt you', 'harm you', 'beat you', 'destroy you',
                        'will rape', 'kidnap', 'murder', 'end you', 'finish you'],
                'medium': ['threaten', 'warning', 'better watch', 'regret', 'consequences',
                          'make you pay', 'get you', 'come after'],
                'low': ['careful', 'watch out']
            },
            'verbal': {
                'high': ['bitch', 'whore', 'slut', 'fuck you', 'bastard', 'cunt',
                        'die', 'worthless', 'disgusting', 'hate you'],
                'medium': ['stupid', 'idiot', 'dumb', 'loser', 'ugly', 'fat',
                          'shut up', 'pathetic', 'useless'],
                'low': ['annoying', 'weird', 'strange']
            },
            'physical': {
                'high': ['hit me', 'punched', 'kicked', 'slapped', 'pushed me down',
                        'threw at me', 'grabbed me', 'choked', 'beaten'],
                'medium': ['pushed', 'shoved', 'grabbed', 'blocked my way', 'cornered',
                          'touched without permission', 'invaded space'],
                'low': ['bumped', 'brushed against']
            },
            'cyber': {
                'high': ['doxx', 'revenge porn', 'leaked photos', 'hacked account',
                        'posted private', 'shared without consent', 'impersonat'],
                'medium': ['cyberbully', 'online harassment', 'trolling', 'spam messages',
                          'fake profile', 'screenshot and share'],
                'low': ['unfriend', 'block', 'report']
            },
            'stalking': {
                'high': ['following me', 'watching me', 'tracking', 'spying',
                        'outside my house', 'knows where i live', 'follows me home'],
                'medium': ['keeps showing up', 'everywhere i go', 'monitors',
                          'checking on me', 'obsessed'],
                'low': ['coincidence', 'ran into']
            },
            'workplace': {
                'high': ['fired for refusing', 'promotion for sexual', 'quid pro quo',
                        'job depends on', 'career threat'],
                'medium': ['hostile environment', 'discriminat', 'unfair treatment',
                          'excluded', 'singled out', 'passed over'],
                'low': ['uncomfortable at work', 'awkward']
            },
            'repetition': {
                'high': ['every day', 'constantly', 'wont stop', 'keeps doing', 'repeatedly',
                        'multiple times', 'again and again', 'despite saying no'],
                'medium': ['several times', 'few times', 'more than once', 'continues'],
                'low': ['twice', 'couple times']
            }
        }
        
        # Patterns for detecting harmful intent
        self.intent_patterns = [
            (r'\b(wont?|will not|don\'t|didnt?|doesn\'t|refuse[ds]?|wouldn\'t)\s+(stop|leave|listen)', 'ignoring_boundaries'),
            (r'\b(asked?|told|said)\s+(to\s+)?(stop|no|leave)', 'boundary_set'),
            (r'\b(force[ds]?|made me|coerce[ds]?|pressure[ds]?)', 'coercion'),
            (r'\b(threatens?|threatening|warned)', 'threat'),
            (r'\b(scared?|afraid|fear|terrified)', 'emotional_impact'),
            (r'\b(without\s+(consent|permission|asking))', 'no_consent'),
            (r'\b(keeps?|keep|constantly|repeatedly|won\'t stop|multiple times)', 'repetition_detected'),
        ]
    
    def _load_or_create_model(self):
        """Load pre-trained model or create a new one with training data."""
        model_path = 'harassment_model.pkl'
        
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            # Create and train a new model
            return self._train_model()
    
    def _train_model(self):
        """Train ML model with sample data."""
        # Training data with diverse examples
        training_data = [
            # Sexual harassment
            ("My boss keeps making sexual comments about my body", "sexual"),
            ("A colleague sent me explicit photos without my consent", "sexual"),
            ("Someone touched me inappropriately at work", "sexual"),
            ("They keep asking me out despite me saying no multiple times", "sexual"),
            
            # Threats
            ("They said they will hurt me if I don't comply", "threat"),
            ("I received messages saying they know where I live and will come after me", "threat"),
            ("Someone threatened to leak my private photos", "threat"),
            ("They warned me there will be consequences if I speak up", "threat"),
            
            # Verbal harassment
            ("My colleague constantly calls me derogatory names", "verbal"),
            ("They yell at me and insult me in front of others", "verbal"),
            ("Someone keeps making racist comments towards me", "verbal"),
            
            # Physical harassment
            ("A person pushed me against the wall", "physical"),
            ("Someone keeps blocking my path and cornering me", "physical"),
            ("They grabbed my arm forcefully when I tried to leave", "physical"),
            
            # Cyber harassment
            ("Someone created a fake profile pretending to be me", "cyber"),
            ("I'm receiving hundreds of hateful messages online", "cyber"),
            ("My private information was posted online without permission", "cyber"),
            
            # Stalking
            ("Someone has been following me for weeks", "stalking"),
            ("They show up everywhere I go despite me asking them to stop", "stalking"),
            ("I keep finding them outside my house", "stalking"),
            
            # Workplace harassment
            ("My manager treats me unfairly because of my gender", "workplace"),
            ("I was passed over for promotion after rejecting advances", "workplace"),
            ("The environment at work is hostile and discriminatory", "workplace"),
            
            # Non-harassment (important for reducing false positives)
            ("My colleague and I had a disagreement about a project", "non-harassment"),
            ("I felt uncomfortable when someone gave constructive criticism", "non-harassment"),
            ("There was a misunderstanding with my friend", "non-harassment"),
            ("I'm stressed about work deadlines", "non-harassment"),
            ("Someone accidentally bumped into me", "non-harassment"),
            ("I had an argument with my partner about household chores", "non-harassment"),
            ("My neighbor plays loud music sometimes", "non-harassment"),
            ("I received a rejection email from a job application", "non-harassment"),
            ("Someone disagreed with my opinion in a meeting", "non-harassment"),
            ("I feel anxious about an upcoming presentation", "non-harassment"),
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        # Create pipeline with TF-IDF and Naive Bayes
        model = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
            ('classifier', MultinomialNB())
        ])
        
        model.fit(texts, labels)
        
        # Save model
        with open('harassment_model.pkl', 'wb') as f:
            pickle.dump(model, f)
        
        return model
    
    def _rule_based_check(self, text: str) -> Dict:
        """
        Rule-based keyword matching with severity scoring.
        Returns category, severity, and matched keywords.
        """
        text_lower = text.lower()
        
        category_scores = {}
        matched_keywords = []
        max_severity = 'Low'
        
        for category, severity_dict in self.keywords.items():
            score = 0
            for severity, keywords in severity_dict.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        matched_keywords.append(f"{keyword} ({category}, {severity})")
                        # Weight by severity
                        if severity == 'high':
                            score += 10
                            if max_severity not in ['Critical', 'High']:
                                max_severity = 'High'
                        elif severity == 'medium':
                            score += 5
                            if max_severity == 'Low':
                                max_severity = 'Medium'
                        else:
                            score += 2
            
            if score > 0:
                category_scores[category] = score
        
        # Check for intent patterns
        intent_matches = []
        for pattern, intent_type in self.intent_patterns:
            if re.search(pattern, text_lower):
                intent_matches.append(intent_type)
                # Boost severity if boundaries are being violated
                if intent_type in ['ignoring_boundaries', 'coercion', 'no_consent']:
                    if max_severity == 'Medium':
                        max_severity = 'High'
                    elif max_severity == 'Low':
                        max_severity = 'Medium'
        
        # Determine primary category
        primary_category = max(category_scores, key=category_scores.get) if category_scores else None
        
        # Check for multiple categories (indicates more serious situation)
        if len(category_scores) >= 3:
            max_severity = 'High'
        
        return {
            'category': primary_category,
            'severity': max_severity,
            'score': sum(category_scores.values()),
            'matched_keywords': matched_keywords,
            'intent_matches': intent_matches,
            'category_scores': category_scores
        }
    
    def _ml_classify(self, text: str) -> Tuple[str, float]:
        """
        ML-based classification.
        Returns predicted category and confidence score.
        """
        try:
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            return prediction, confidence
        except:
            return "non-harassment", 0.5
    
    def analyze_incident(self, text: str) -> Dict:
        """
        Main analysis function combining rule-based and ML approaches.
        Returns comprehensive analysis with category, severity, and guidance.
        """
        # Get both analyses
        rule_result = self._rule_based_check(text)
        ml_category, ml_confidence = self._ml_classify(text)
        
        # Determine if harassment
        is_harassment = (
            rule_result['score'] > 0 or 
            (ml_category != 'non-harassment' and ml_confidence > 0.6)
        )
        
        # Determine final category
        if rule_result['category']:
            # Rule-based has higher priority for explicit keywords
            final_category = rule_result['category']
            confidence = min(0.95, 0.7 + (rule_result['score'] / 50))
        else:
            final_category = ml_category
            confidence = ml_confidence
        
        # Map category to display format
        category_display = {
            'sexual': 'Sexual Harassment',
            'threat': 'Threats/Intimidation',
            'verbal': 'Verbal Harassment',
            'physical': 'Physical Harassment',
            'cyber': 'Cyber Harassment',
            'stalking': 'Stalking',
            'workplace': 'Workplace Harassment',
            'non-harassment': 'Non-Harassment'
        }.get(final_category, 'Unclear')
        
        # Determine severity
        severity = rule_result['severity']
        if rule_result['score'] > 20 or len(rule_result.get('category_scores', {})) >= 3:
            severity = 'Critical'
        
        # Generate explanation
        explanation = self._generate_explanation(
            rule_result, ml_category, ml_confidence, is_harassment
        )
        
        # Get indicators
        indicators = []
        if rule_result['matched_keywords']:
            indicators.append("Detected concerning keywords related to harassment")
        if rule_result['intent_matches']:
            for intent in rule_result['intent_matches']:
                intent_text = intent.replace('_', ' ').title()
                indicators.append(f"Pattern detected: {intent_text}")
        if len(rule_result.get('category_scores', {})) >= 2:
            indicators.append("Multiple harassment categories detected")
        
        return {
            'is_harassment': is_harassment,
            'category': category_display,
            'severity': severity,
            'confidence_score': confidence,
            'explanation': explanation,
            'indicators': indicators,
            'rule_score': rule_result['score'],
            'ml_prediction': ml_category,
            'matched_keywords': rule_result['matched_keywords']
        }
    
    def _generate_explanation(self, rule_result: Dict, ml_category: str, 
                            ml_confidence: float, is_harassment: bool) -> str:
        """Generate human-readable explanation of the analysis."""
        
        if not is_harassment:
            return (
                "Based on our analysis, this incident does not appear to contain clear indicators "
                "of harassment. It may be a conflict, misunderstanding, or difficult situation. "
                "However, if you feel unsafe or uncomfortable, your feelings are valid and you "
                "may want to seek support."
            )
        
        explanation_parts = []
        
        if rule_result['matched_keywords']:
            explanation_parts.append(
                f"Our system detected {len(rule_result['matched_keywords'])} concerning keywords "
                "or phrases typically associated with harassment."
            )
        
        if rule_result['intent_matches']:
            explanation_parts.append(
                "We identified patterns suggesting boundaries being violated or harmful intent."
            )
        
        if rule_result['score'] > 15:
            explanation_parts.append(
                "The severity and combination of indicators suggest this is a serious situation "
                "that warrants immediate attention."
            )
        
        if ml_confidence > 0.8:
            explanation_parts.append(
                "Our machine learning model has high confidence in this classification."
            )
        elif ml_confidence < 0.6:
            explanation_parts.append(
                "While our analysis detected concerning elements, the overall context suggests "
                "careful consideration is needed. We recommend documenting the incident and "
                "seeking guidance from trusted sources."
            )
        
        return " ".join(explanation_parts) if explanation_parts else (
            "This situation shows indicators of harassment based on our analysis."
        )
    
    def get_legal_guidance(self, category: str) -> Dict:
        """Provide legal guidance specific to India based on harassment category."""
        
        legal_info = {
            'Sexual Harassment': {
                'applicable_laws': [
                    'Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013',
                    'Indian Penal Code Section 354A - Sexual harassment and punishment',
                    'IPC Section 509 - Word, gesture or act intended to insult the modesty',
                    'IPC Section 294 - Obscene acts and songs'
                ],
                'actions': [
                    'File complaint with Internal Complaints Committee (ICC) if workplace',
                    'File written complaint with Local Complaints Committee (LCC)',
                    'File FIR at police station',
                    'Contact National Commission for Women (NCW): 7827-170-170',
                    'Seek legal counsel for civil remedies'
                ]
            },
            'Threats/Intimidation': {
                'applicable_laws': [
                    'IPC Section 503 - Criminal intimidation',
                    'IPC Section 506 - Punishment for criminal intimidation',
                    'IPC Section 507 - Criminal intimidation by anonymous communication',
                    'IPC Section 383 - Extortion'
                ],
                'actions': [
                    'File FIR immediately with police',
                    'Preserve all evidence (messages, recordings, emails)',
                    'Seek protection order if needed',
                    'Inform local police station about the threats',
                    'Consider personal safety measures'
                ]
            },
            'Physical Harassment': {
                'applicable_laws': [
                    'IPC Section 323 - Punishment for voluntarily causing hurt',
                    'IPC Section 354 - Assault or criminal force to woman with intent to outrage her modesty',
                    'IPC Section 341 - Punishment for wrongful restraint',
                    'IPC Section 504 - Intentional insult with intent to provoke breach of peace'
                ],
                'actions': [
                    'Seek immediate medical attention and get medical certificate',
                    'File FIR with police',
                    'Document injuries with photographs',
                    'Gather witness statements',
                    'Apply for restraining order if needed'
                ]
            },
            'Cyber Harassment': {
                'applicable_laws': [
                    'IT Act Section 66A - Offensive messages through communication service',
                    'IT Act Section 66E - Violation of privacy',
                    'IT Act Section 67 - Publishing obscene material in electronic form',
                    'IPC Section 354C - Voyeurism',
                    'IPC Section 354D - Stalking (including cyber stalking)'
                ],
                'actions': [
                    'Report to cybercrime.gov.in immediately',
                    'Take screenshots of all evidence',
                    'File complaint with Cyber Crime Cell',
                    'Report to social media platforms',
                    'Contact Cyber Crime Helpline: 1930',
                    'Preserve digital evidence'
                ]
            },
            'Stalking': {
                'applicable_laws': [
                    'IPC Section 354D - Stalking',
                    'Protection of Women from Domestic Violence Act, 2005 (if applicable)'
                ],
                'actions': [
                    'File FIR with police immediately',
                    'Maintain detailed log of all incidents',
                    'Apply for restraining order',
                    'Inform workplace and residence security',
                    'Vary daily routines and routes',
                    'Install security cameras if possible'
                ]
            },
            'Workplace Harassment': {
                'applicable_laws': [
                    'Sexual Harassment of Women at Workplace Act, 2013',
                    'Equal Remuneration Act, 1976',
                    'Industrial Employment (Standing Orders) Act, 1946',
                    'Relevant labour laws and employment acts'
                ],
                'actions': [
                    'File complaint with Internal Complaints Committee (ICC)',
                    'Document all incidents in writing',
                    'Send formal complaint to HR department',
                    'Contact Labour Commissioner if needed',
                    'Reach out to State Women\'s Commission',
                    'Consult employment lawyer'
                ]
            },
            'Verbal Harassment': {
                'applicable_laws': [
                    'IPC Section 504 - Intentional insult with intent to provoke breach of peace',
                    'IPC Section 509 - Word, gesture or act intended to insult modesty',
                    'IPC Section 294 - Obscene acts and songs'
                ],
                'actions': [
                    'Document all incidents with dates and details',
                    'Gather witness statements',
                    'File complaint with police if threats involved',
                    'Report to appropriate authority (workplace, school, etc.)',
                    'Seek legal counsel for defamation if applicable'
                ]
            }
        }
        
        return legal_info.get(category, {
            'applicable_laws': ['Consult with a lawyer for specific legal provisions'],
            'actions': ['Document the incident', 'Seek legal consultation', 'File police complaint if needed']
        })
    
    def get_evidence_tips(self) -> List[str]:
        """Provide evidence collection guidance."""
        return [
            "Document everything: dates, times, locations, what was said/done",
            "Save all messages, emails, screenshots, photos, and videos",
            "Take photos of any injuries or property damage",
            "Record names and contact information of any witnesses",
            "Keep a detailed journal of all incidents",
            "Save any physical evidence (letters, gifts, etc.)",
            "Back up all digital evidence in multiple locations",
            "Get medical documentation if physically harmed",
            "Keep original copies of all evidence",
            "Do not delete anything, even if it's distressing"
        ]
    
    def get_helplines(self, category: str) -> List[Dict]:
        """Provide relevant helplines based on category."""
        
        all_helplines = [
            {
                'name': 'National Emergency Number',
                'number': '112',
                'description': 'For immediate emergency assistance (24/7)'
            },
            {
                'name': 'Women Helpline',
                'number': '1091',
                'description': 'For women in distress (24/7)'
            },
            {
                'name': 'National Commission for Women',
                'number': '7827-170-170',
                'description': 'For complaints and guidance on women-related issues'
            },
            {
                'name': 'Domestic Violence Helpline',
                'number': '181',
                'description': 'For domestic abuse and violence support'
            },
            {
                'name': 'Cyber Crime Helpline',
                'number': '1930',
                'description': 'For reporting cybercrimes and online harassment'
            },
            {
                'name': 'Police Control Room',
                'number': '100',
                'description': 'For reporting crimes and seeking police assistance'
            },
            {
                'name': 'Child Helpline',
                'number': '1098',
                'description': 'For children and adolescents in need of help'
            }
        ]
        
        # Filter relevant helplines based on category
        relevant_helplines = []
        
        if 'Cyber' in category:
            relevant_helplines.append(all_helplines[4])  # Cyber Crime
        if 'Sexual' in category or 'Workplace' in category:
            relevant_helplines.append(all_helplines[2])  # NCW
        if 'Physical' in category or 'Threat' in category:
            relevant_helplines.append(all_helplines[0])  # Emergency
            relevant_helplines.append(all_helplines[5])  # Police
        
        # Always add women helpline
        if all_helplines[1] not in relevant_helplines:
            relevant_helplines.append(all_helplines[1])
        
        return relevant_helplines if relevant_helplines else all_helplines[:3]
