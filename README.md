# Tabula: The DAO Intelligence Hub

![1  banner](https://github.com/user-attachments/assets/ea8943e6-863d-4146-8309-da0640702959)


**Intuitive, impactful, and actually autonomous.**

Tabula is an AI-powered governance hub on [Base](https://www.base.org/) that transforms raw DAO data into actionable insights, enabling seamless participation, intelligent delegation, and informed decision-making.

## Index

1. [Overview](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#1-overview)
2. [Core Features](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#2-core-features)
3. [User Flow](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#3-user-flow)
4. [Agent Architecture](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#4-agent-architecture)
5. [Advanced Features](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#5-advanced-features)
6. [Technical Architecture](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#6-technical-architecture)
7. [Deployments](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#7-deployments)
8. [Development Status](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#8-development-status)
9. [Contact](https://github.com/MihRazvan/agentic_hackathon/blob/main/README.md#9-contact)

### Annex

[Demo](https://youtu.be/BBEOu9iXQXo?si=9rxrMi5u_Tvvl3sF) | [Prototype App](https://tabula.opsec.run/) | [Slide Deck](https://github.com/MihRazvan/agentic_hackathon/blob/main/docs/slide-deck.md) | [Contribution Guide](https://github.com/MihRazvan/agentic_hackathon/blob/main/docs/contribution-guide.md) | [Design Files](https://github.com/MihRazvan/agentic_hackathon/blob/main/docs/design-files.md) | [UI Mockups](https://github.com/MihRazvan/agentic_hackathon/blob/main/docs/ui-mockups.md) | [Local Testing Guide](https://github.com/MihRazvan/agentic_hackathon/blob/main/docs/local-testing-guide.md)

## 1. Overview

In the complex world of Decentralized Autonomous Organizations (DAOs), participants face several critical challenges:

- **Information Overload:** Navigating through multiple DAOs and their numerous proposals can be overwhelming.
- **Complex Proposal Analysis:** Understanding the implications of various proposals requires significant effort.
- **Time-Consuming Participation:** Active involvement in governance processes demands substantial time and attention (usually not directly compensated).
- **Fragmented Tools and Data:** The lack of unified platform leads to inefficiencies and missed opportunities.

**TABULA** addresses these challenges by providing an intelligent, unified dashboard that transforms how users engage with DAOs. With our approach, we transmute raw governance data into clear, actionable insights.

![1  banner (2)](https://github.com/user-attachments/assets/8e2beb15-be4e-4611-ad94-297c2ae27b36)

---

## 2. Core Features

### Intelligent Dashboard

1. **Comprehensive Delegation Overview:** Gain a holistic view of your DAO delegations and discover potential opportunities.
2. **Governance Health Metrics:** Monitor participation rates and overall governance health.
3. **Event Timelines:** Visualize upcoming governance events with intuitive timelines.
4. **Delegation Impact Tracking:** Assess the influence of your delegations over time.
5. **DAO Performance Comparison:** Compare and analyze the performance of different DAOs.

### Smart Updates Hub

1. **Priority-Based Notifications:** Receive updates categorized as Urgent, Important, or FYI.
2. **AI-Curated Summaries:** Access synthesized information on DAO proposals, treasury updates, and governance changes.
3. **Impact Analysis:** Understand the potential effects of major governance decisions.
4. **Social Sentiment Tracking:** Stay informed about community discussions and sentiments.
5. **Custom Notifications:** Set up alerts for critical updates tailored to your interests.

### Governance Assistant (AI-Powered Chat)

1. **Proposal Impact Analysis:** Break down the implications of specific proposals.
2. **Governance Simulation:** Explore potential outcomes if a proposal passes.
3. **Delegate Assistance:** Receive synthesized information on existing DAO delegates, complete with performance scores, to make informed delegation decisions.
4. **Treasury Visualization:** View detailed allocations of DAO treasuries.
5. **Direct Action Integration:** Execute votes and delegations seamlessly through the chat interface.
6. **ELI5 Mode:** Get simplified explanations for complex proposals.

---

## 3. User Flow

![4  user flow](https://github.com/user-attachments/assets/e626737f-5ccc-4e5b-91b1-5d4165f5f303)

---

## 4. Agent Architecture

### Tally Agent (Data & Analytics)

1. **Architecture:**
- **Framework:** AgentKit with Tally API integration
- **Core Function:** Governance data retrieval and analytics

2. **Key Components:**
- **TallyClient:** Handles GraphQL queries to Tally API
- **Analytics Engine:** Processes DAO data
- **Response Formatter:** Structures data for frontend

3. **Capabilities:**
- *Fetch proposal data*
- *Analyze delegate performance*
- *Track treasury movements*
- *Monitor governance activity*

### Alchemist Chatbot Agent (User Interaction)

1. **Architecture:**
- **Framework:** AgentKit + LangChain + Autonome deployment
- **Core Function:** Natural language DAO interaction

2. **Components:**
- **LLM Integration:** GPT-4 for natural language processing
- **CDP Toolkit:** For on-chain capabilities
- **Intent Classifier:** Understands user requests
- **Action Generator:** Prepares transaction parameters

3. **Capabilities:**
- *Natural language DAO interactions*
- *Proposal explanations (ELI5)*
- *Transaction preparation*
- *Delegation guidance*

### LLM Updates Curator Agent (Content)

1. **Architecture:**
- **Framework:** AgentKit + LangChain for content generation
- **Core Function:** Curate and prioritize DAO updates

2. **Components:**
- **Update Analyzer:** Assesses update importance
- **Content Generator:** Creates summaries
- **Priority Engine:** Ranks updates
- **Category Classifier:** Tags content type

3. **Capabilities:**
- *Analyze proposal impacts*
- *Generate summaries*
- *Prioritize updates (urgent/important/fyi)*
- *Create action recommendations*

---

## 5. Advanced Features

### Delegate-to-User Matchmaking

1. **Delegate Analysis:** Utilize the Tally API to examine delegate voting histories and statements.
2. **Profiles:** Fetch delegate profiles and match them with user preferences.
3. **Recommendation System:** Suggest delegates based on:
  - Voting history alignment
  - Activity levels
  - Governance philosophy
  - Domain expertise

### Post-Execution Transaction Tracking

1. **Automatic Monitoring:** Keep track of proposal executions automatically.
2. **Impact Analysis:** Evaluate the effects of implemented proposals.
3. **Treasury Movement Tracking:** Monitor treasury changes following proposal execution.
4. **AI-Generated Reports:** Compare intended outcomes with actual results through detailed reports.

### Aggregation and Context Focusing

1. **AI-Curated Summaries:** Access synthesized governance discussions.
2. **Key Decision Highlights:** Identify and focus on crucial decision points.
3. **Proposal Pattern Tracking:** Observe trends and patterns in proposals.
4. **Historical Context Provision:** Gain background information to better understand current proposals.

---

## 6. Technical Architecture

- **Base:** Network of choice for deployment.
- **Tally API:** Integrates core DAO data seamlessly.
- **LangChain:** Serves as the agent framework.
- **AgentKit:** Facilitates AI-powered governance interactions.
- **OnchainKit / Smart Wallet:** Provides a seamless frontend experience.
- **Autonome:** Deploys advanced AI capabilities.
- **OneSec:** Ensures secure DApp deployment.

![6  tech stack](https://github.com/user-attachments/assets/e50373fc-6c27-4091-acbe-10f5c53b28b1)

---

## 7. Deployments

1. [Autonome deployment](https://autonome.alt.technology/agent-bjzmlr)
2. [OneSec deployment](https://tabula.opsec.run/)

---

## 8. Development Status

This project has been built for ETHGlobal Agentic Hackathon 2025.
Further development envisioned is additional review and optimization, audit, exploring deployment across the Superchain and beyond!

---

## 9. Contact

**Email:** jensei.eth@protonmail.com / razvan.mihailescu1996@gmail.com

**Twitter:** [jensei_](https://x.com/jensei_) / [magentoooo](https://x.com/magentoooo)

