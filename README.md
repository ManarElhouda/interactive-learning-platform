AI-Driven Cognitive and Interactive Learning Framework for Individuals with Down Syndrome

Overview

This project presents a comprehensive AI-driven framework designed to support individuals with Down Syndrome

Unlike single-task systems, this solution integrates multiple AI modules to address:

Communication difficulties
Learning challenges
Emotional monitoring
Medical analysis
The goal is to deliver a unified, adaptive, and intelligent assistive system for both users and caregivers.

Key Features

Speech assistance and pronunciation correction
Adaptive and personalized learning
Emotion and behavior monitoring
Brain MRI anomaly detection
Explainable AI for transparency
Complete AI Solutions

Speech & Communication Solution
This module improves communication abilities by:

Using Whisper for speech recognition

Handling unintelligible or atypical speech

Detecting mispronunciations using:

GOP (Goodness of Pronunciation)
CTC alignment
Providing real-time pronunciation correction

Adaptive Learning Solution
This module personalizes the learning experience:

Reinforcement Learning (DQN)
Neutrosophic + Fuzzy clustering
Dynamic difficulty adaptation
Learner profiling based on performance
Emotion & Behavior Solution
This module monitors user state:

Facial emotion recognition (EfficientNet + Transformer)

Detection of:

Frustration
Engagement
Attention tracking (eye tracking)

Behavioral data logging

Medical Analysis Solution
This module provides clinical insights:

Brain MRI anomaly detection
Diffusion models (DDPM / DDIM)
Reconstruction of normal-like MRI
Heatmap-based anomaly localization
Explainable AI Solution
Ensures transparency of AI decisions:

Grad-CAM visualization

Highlights important brain regions:

Hippocampus
Cerebellum
Cortex
Ventricles
Global System Workflow

Input:

Speech
Images (face)
Behavioral signals
MRI scans
Processing:

Each module analyzes its modality
Adaptation:

Learning adjusts in real-time
Feedback is generated
Output:

Speech correction
Learning recommendations
Emotion state
Medical insights
Tech Stack

AI / Deep Learning: PyTorch, TensorFlow
Speech: Whisper, wav2vec2
Vision: EfficientNet, MediaPipe
Diffusion Models: DDPM, DDIM
Backend: FastAPI
Frontend: React + TypeScript
Dataset

Module	Data Type	Size
Speech	Audio (Tunisian dialect)	536 samples
Emotion	Facial images	1005 images
MRI	Brain scans	4756 EU + 111 DS
Behavioral	Interaction logs	Ongoing
Challenges

Limited datasets (especially Down Syndrome)
Multimodal integration complexity
Real-time processing constraints
Ethics

Data anonymization
User consent
Human supervision
Future Work

Deployment in real environments
Larger datasets
Improved personalization
Clinical validation
## 🌐 Live Demo

Our platform is available online and accessible through Railway:

🔗 [Visit our website]([TON_LIEN_RAILWAY](https://frontend-production-ce37.up.railway.app/)

---

## 💡 About the Project

This project was developed with passion and dedication to create an inclusive educational experience for children with Down syndrome.

We hope our solution can make learning more engaging, interactive, and accessible for every child.

---

## 👨‍💻 Team

Developed by our team as part of our academic and innovation journey.
