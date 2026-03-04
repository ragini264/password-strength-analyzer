# create_password_dataset.py
import pandas as pd
import numpy as np
import random
import string
import secrets
from sklearn.utils import shuffle

class PasswordDatasetGenerator:
    def __init__(self):
        self.strength_labels = {
            0: 'Very Weak',
            1: 'Weak', 
            2: 'Medium',
            3: 'Strong',
            4: 'Very Strong'
        }
    
    def generate_weak_passwords(self):
        passwords = []
        strengths = []
        
        # Common weak passwords
        common_weak = [
            '123456', 'password', '12345678', 'qwerty', '123456789',
            '12345', '1234', '111111', '1234567', 'dragon',
            '123123', 'baseball', 'abc123', 'football', 'monkey',
            'letmein', 'shadow', 'master', '666666', 'qwertyuiop',
            '123321', 'mustang', '1234567890', 'michael', 'superman'
        ]
        
        for pwd in common_weak:
            passwords.append(pwd)
            strengths.append(0)  # Very weak
            
        # Generate sequential patterns
        for i in range(100):
            passwords.append(str(i) * 3)
            strengths.append(0)
            passwords.append('abc' + str(i))
            strengths.append(0)
            
        # Keyboard patterns
        keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', 'qazwsx']
        for pattern in keyboard_patterns:
            passwords.append(pattern)
            strengths.append(0)
            passwords.append(pattern + '123')
            strengths.append(1)  # Weak
        
        # Weak variations
        for base in common_weak[:20]:
            for i in range(3):
                passwords.append(base + str(i))
                strengths.append(1)
                passwords.append(str(i) + base)
                strengths.append(1)
        
        return passwords, strengths
    
    def generate_medium_passwords(self):
        passwords = []
        strengths = []
        
        base_words = ['pass', 'secure', 'safe', 'guard', 'shield', 'lock']
        special_chars = ['!', '@', '#', '$', '%']
        
        for word in base_words:
            for i in range(20):
                # Word + numbers + special char
                pwd = word.capitalize() + str(i) + random.choice(special_chars)
                passwords.append(pwd)
                strengths.append(2)  # Medium
                
                # Mixed case + numbers
                pwd = word.upper() + str(i*10) + word.lower()
                passwords.append(pwd)
                strengths.append(2)
        
        # Random medium passwords
        for _ in range(100):
            length = random.randint(8, 10)
            pwd = ''.join(random.choice(string.ascii_letters + string.digits) 
                         for _ in range(length))
            if (any(c.islower() for c in pwd) and 
                any(c.isupper() for c in pwd) and 
                any(c.isdigit() for c in pwd)):
                passwords.append(pwd)
                strengths.append(2)
        
        return passwords, strengths
    
    def generate_strong_passwords(self):
        passwords = []
        strengths = []
        
        # Strong passwords
        for i in range(150):
            length = random.randint(10, 12)
            pwd = ''.join(random.choice(string.ascii_letters + string.digits + '!@#$%') 
                         for _ in range(length))
            if (sum(1 for c in pwd if c.islower()) >= 2 and
                sum(1 for c in pwd if c.isupper()) >= 2 and
                sum(1 for c in pwd if c.isdigit()) >= 2 and
                sum(1 for c in pwd if c in '!@#$%') >= 1):
                passwords.append(pwd)
                strengths.append(3)  # Strong
        
        # Very strong passwords
        for i in range(150):
            length = random.randint(14, 18)
            pwd = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*') 
                         for _ in range(length))
            passwords.append(pwd)
            strengths.append(4)  # Very strong
        
        return passwords, strengths
    
    def calculate_features(self, password):
        features = {
            'length': len(password),
            'uppercase_count': sum(1 for c in password if c.isupper()),
            'lowercase_count': sum(1 for c in password if c.islower()),
            'digit_count': sum(1 for c in password if c.isdigit()),
            'special_count': sum(1 for c in password if c in string.punctuation),
            'has_uppercase': int(any(c.isupper() for c in password)),
            'has_lowercase': int(any(c.islower() for c in password)),
            'has_digits': int(any(c.isdigit() for c in password)),
            'has_special': int(any(c in string.punctuation for c in password))
        }
        
        # Calculate entropy
        if len(password) == 0:
            features['entropy'] = 0
        else:
            char_count = {}
            for char in password:
                char_count[char] = char_count.get(char, 0) + 1
            entropy = 0
            for count in char_count.values():
                p = count / len(password)
                if p > 0:
                    entropy -= p * np.log2(p)
            features['entropy'] = entropy
        
        return features
    
    def generate_complete_dataset(self, total_samples=1500):
        print("Generating password dataset...")
        
        # Generate passwords of different strengths
        weak_passwords, weak_strengths = self.generate_weak_passwords()
        medium_passwords, medium_strengths = self.generate_medium_passwords()
        strong_passwords, strong_strengths = self.generate_strong_passwords()
        
        # Combine all passwords
        all_passwords = weak_passwords + medium_passwords + strong_passwords
        all_strengths = weak_strengths + medium_strengths + strong_strengths
        
        # Remove duplicates
        seen = set()
        unique_passwords = []
        unique_strengths = []
        for pwd, strength in zip(all_passwords, all_strengths):
            if pwd not in seen:
                seen.add(pwd)
                unique_passwords.append(pwd)
                unique_strengths.append(strength)
        
        # Shuffle
        unique_passwords, unique_strengths = shuffle(
            unique_passwords, unique_strengths, random_state=42
        )
        
        # Take requested number of samples
        if len(unique_passwords) > total_samples:
            unique_passwords = unique_passwords[:total_samples]
            unique_strengths = unique_strengths[:total_samples]
        
        print(f"Generated {len(unique_passwords)} unique passwords")
        
        # Calculate features
        feature_data = []
        for password in unique_passwords:
            features = self.calculate_features(password)
            feature_data.append(features)
        
        # Create DataFrame
        df = pd.DataFrame({
            'password': unique_passwords,
            'strength': unique_strengths
        })
        
        # Add feature columns
        for feature_name in feature_data[0].keys():
            df[feature_name] = [features[feature_name] for features in feature_data]
        
        # Add strength labels
        df['strength_label'] = df['strength'].map(self.strength_labels)
        
        # Display statistics
        self.print_dataset_stats(df)
        
        return df
    
    def print_dataset_stats(self, df):
        print("\nDataset Statistics:")
        print("=" * 40)
        print(f"Total passwords: {len(df)}")
        print("\nStrength Distribution:")
        strength_counts = df['strength_label'].value_counts().sort_index()
        for strength, count in strength_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {strength}: {count} ({percentage:.1f}%)")
        
        print("\nFeature Overview:")
        print(f"  Average length: {df['length'].mean():.1f} characters")
        print(f"  Average entropy: {df['entropy'].mean():.2f}")
        print(f"  Passwords with special chars: {df['has_special'].sum()}")

def create_password_csv():
    generator = PasswordDatasetGenerator()
    df = generator.generate_complete_dataset(1000)
    
    csv_path = 'data/passwords.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nDataset saved to: {csv_path}")
    return df

if __name__ == "__main__":
    create_password_csv()
