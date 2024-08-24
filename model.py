import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split

# Example Dataset class
class RealScheduleDataset(Dataset):
    def __init__(self, csv_file):
        # Load the dataset from the CSV file
        self.data = pd.read_csv(csv_file)
        
        # Extract features: major, year, morning/night preference, courses taken, GPA, credits
        majors = self.data['major'].values.reshape(-1, 1)
        year = self.data['year'].values
        time_preference = self.data['morning_night'].apply(lambda x: 1 if x == 'Morning' else 0).values
        courses_taken = self.data['courses_taken'].values  # Assuming this is a numeric or binary feature
        gpa = self.data['gpa'].values
        credits = self.data['credits'].values

        # Encode categorical data (like majors)
        major_encoder = OneHotEncoder(sparse=False)
        encoded_majors = major_encoder.fit_transform(majors)

        # Normalize GPA and credits
        scaler = StandardScaler()
        normalized_gpa = scaler.fit_transform(gpa.reshape(-1, 1))
        normalized_credits = scaler.fit_transform(credits.reshape(-1, 1))

        # Combine all features into a single feature matrix
        self.features = torch.tensor(
            np.hstack((encoded_majors, year.reshape(-1, 1), time_preference.reshape(-1, 1), courses_taken.reshape(-1, 1), normalized_gpa, normalized_credits)),
            dtype=torch.float32
        )

        # Extract and convert labels (combination of courses recommended by the model)
        self.labels = torch.tensor(
            np.array([list(map(int, label.split(','))) for label in self.data['recommended_courses']]),  
            dtype=torch.float32
        )

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]
    
    def inverse_transform_label(self, label):
        """
        Converts a one-hot encoded label back to its original format (e.g., course names).
        """
        return [i for i, val in enumerate(label) if val == 1]

    def split_data(self, val_size=0.2, test_size=0.2):
        """
        Splits the dataset into training, validation, and test sets.
        """
        total_size = len(self.data)
        val_split = int(total_size * val_size)
        test_split = int(total_size * test_size)
        train_split = total_size - val_split - test_split

        train_data, val_data, test_data = torch.utils.data.random_split(
            self, [train_split, val_split, test_split]
        )
        return train_data, val_data, test_data

    def handle_missing_data(self):
        """
        Fills or removes missing data from the dataset.
        """
        self.data.fillna(method='ffill', inplace=True)  # Forward fill as an example

    def add_new_data(self, new_data_df):
        """
        Adds new data to the existing dataset without needing to reload everything.
        """
        self.data = pd.concat([self.data, new_data_df], ignore_index=True)
        self.features, self.labels = self._preprocess_data()

# Neural Network model
class ScheduleRecommendationModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ScheduleRecommendationModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.fc3(x)
        return x

# Data Preparation
# Example raw data (this would typically come from a CSV or database)
raw_features = [
    ["Computer Science", 3, "Morning", 1, 0.85],  # Example row
    ["Data Science", 2, "Night", 0, 0.75],       # Example row
    # Add more rows here
]

raw_labels = [
    [1, 0, 0, 1, 0],  # One-hot encoded labels for course recommendations
    [0, 1, 1, 0, 1],  # Example output
    # Add more labels here
]

# Convert categorical features (like "Computer Science") to numerical
majors = [row[0] for row in raw_features]
major_encoder = OneHotEncoder(sparse=False)
encoded_majors = major_encoder.fit_transform(np.array(majors).reshape(-1, 1))

# Convert "Morning/Night" preference to binary
time_preference = [1 if row[2] == "Morning" else 0 for row in raw_features]

# Prepare remaining features (year, courses taken, GPA)
years = [row[1] for row in raw_features]
courses_taken = [row[3] for row in raw_features]
gpa = [row[4] for row in raw_features]

# Normalize the GPA
scaler = StandardScaler()
gpa = scaler.fit_transform(np.array(gpa).reshape(-1, 1))

# Combine all features into a single feature matrix
features = np.hstack((encoded_majors, np.array(years).reshape(-1, 1), np.array(time_preference).reshape(-1, 1), np.array(courses_taken).reshape(-1, 1), gpa))

# Convert labels to a numpy array
labels = np.array(raw_labels)

# Split data into train, validation, and test sets
train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2, random_state=42)
train_features, val_features, train_labels, val_labels = train_test_split(train_features, train_labels, test_size=0.2, random_state=42)

# Create Dataset and DataLoader objects
train_dataset = ScheduleDataset(train_features, train_labels)
val_dataset = ScheduleDataset(val_features, val_labels)
test_dataset = ScheduleDataset(test_features, test_labels)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Initialize the model, loss function, and optimizer
input_size = train_features.shape[1]
hidden_size = 32
output_size = labels.shape[1]
model = ScheduleRecommendationModel(input_size, hidden_size, output_size)
criterion = nn.MSELoss()  
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training loop with validation
num_epochs = 50
for epoch in range(num_epochs):
    model.train()
    for batch_features, batch_labels in train_loader:
        outputs = model(batch_features)
        loss = criterion(outputs, batch_labels)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Validation
    model.eval()
    with torch.no_grad():
        val_loss = 0
        for batch_features, batch_labels in val_loader:
            outputs = model(batch_features)
            val_loss += criterion(outputs, batch_labels).item()
        val_loss /= len(val_loader)
    
    if (epoch+1) % 10 == 0:
        print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Validation Loss: {val_loss:.4f}')

print("Training complete!")

# Testing
model.eval()
with torch.no_grad():
    test_loss = 0
    for batch_features, batch_labels in test_loader:
        outputs = model(batch_features)
        test_loss += criterion(outputs, batch_labels).item()
    test_loss /= len(test_loader)
print(f'Test Loss: {test_loss:.4f}')

# Saving the model
torch.save(model.state_dict(), "schedule_recommendation_model.pth")
