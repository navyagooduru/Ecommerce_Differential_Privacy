# Protecting Shopping Preferences with Differential Privacy

A privacy-preserving e-commerce web application that demonstrates how **Differential Privacy** can be applied to shopping interaction data while still supporting useful analytics and product recommendations.

The project combines a basic e-commerce system with a privacy layer based on the **Laplace Mechanism** to protect aggregate shopping statistics.

---

## Project Overview

Modern e-commerce platforms collect large amounts of user interaction data such as:

- Product views
- Add-to-cart activities
- Purchases
- Shopping preferences
- Product interactions
- User behavior

This information is valuable for analytics and recommendations, but directly exposing individual-level shopping behavior can create privacy concerns.

This project explores a privacy-preserving approach where shopping interactions are collected and analyzed, while **Differential Privacy is applied to aggregate statistics before they are used for analytics**.

The goal is to achieve a balance between:

> **Privacy + Data Utility + Personalization**

---

## Key Features

### E-Commerce Features

- User registration
- User login and logout
- Product browsing
- Category-based product browsing
- Product search
- Product details
- Add products to cart
- Increase/decrease cart quantity
- Checkout
- Order placement
- Order history
- Shopping interaction tracking

### Privacy Features

- Differential Privacy for shopping analytics
- Laplace Mechanism
- Configurable privacy parameter (epsilon)
- Sensitivity-based noise calculation
- Original vs protected statistics
- Privacy-preserving interaction analytics

### Analytics Features

The system analyzes:

- Product views
- Add-to-cart activity
- Purchases
- Category-level shopping activity
- Product interaction patterns
- Popular products
- Shopping trends

### Recommendation Features

The recommendation system uses shopping interactions to identify relevant product recommendations while considering the user's recent shopping activity and preferred product category.

---

## System Architecture

```text
                    USER
                     |
                     v
          +----------------------+
          |   E-COMMERCE UI      |
          |   HTML / CSS / JS    |
          +----------+-----------+
                     |
                     v
          +----------------------+
          |    FLASK BACKEND     |
          +----------+-----------+
                     |
                     v
          +----------------------+
          |   SHOPPING DATA      |
          |      SQLite          |
          +----------+-----------+
                     |
                     v
       +-----------------------------+
       |   DIFFERENTIAL PRIVACY      |
       |       LAPLACE MECHANISM     |
       +-------------+---------------+
                     |
                     v
       +-----------------------------+
       | PRIVACY-PROTECTED SHOPPING  |
       |           DATA              |
       +-------------+---------------+
                     |
                     v
       +-----------------------------+
       |       DATA ANALYTICS        |
       +-------------+---------------+
                     |
             +-------+-------+
             |               |
             v               v
     SHOPPING TRENDS    PRODUCT
       & ANALYTICS    RECOMMENDATIONS
