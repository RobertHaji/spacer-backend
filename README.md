# ✨Spacer App✨ – Backend API (Flask & SQLAlchemy)

A simple RESTful backend for Spacer App, built using Flask, SQLAlchemy, and relational database models. It powers user management, space listings, bookings, payments, categories, and images.

---

## ⚙️ Overview

- Modular design with one model/resource per component:
  - **User**, **Space**, **Booking**, **Category**, **Payment**, **Image**
- Database powered by SQLAlchemy with a naming convention for tables and constraints
- Models serialize nicely using `SerializerMixin`
- Blueprints for each resource (not shown here) connect views logically
- JWT-based authentication (e.g., login, protected routes)
- Payment logic is simulated—handled simply via the `Payment` model

---

## 🚧 Data Models & Relationships

- **User**: can be `admin` or `user`, related to bookings and categories  
- **Space**: belongs to a category and user (also admin), has many bookings and images  
- **Booking**: links a user and a space; includes guest count, hours, location  
- **Category**: named types created by an admin; a category holds many spaces  
- **Payment**: one-to-one with a booking for invoice simulation  
- **Image**: multiple images tied to each space  

Timestamp fields (`created_at`, `updated_at`) track creation and modifications.

 
---

## 🔧 Getting Started

1. Clone the repo:
   On your terminal, 
   git clone 
   cd spacer-backend

