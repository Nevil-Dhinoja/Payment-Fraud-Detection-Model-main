# 🔧 Defraudo - Backend Server

<div align="center">

![Node.js](https://img.shields.io/badge/Node.js-16+-339933?style=for-the-badge&logo=node.js&logoColor=white)
![Express](https://img.shields.io/badge/Express.js-4.x-000000?style=for-the-badge&logo=express&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

**RESTful API Backend for the AI-Powered Fraud Detection System**

</div>

## ✨ Features

- **🔐 JWT Authentication** - Secure user authentication with tokens
- **📝 User Management** - Registration and login endpoints
- **💳 Transaction API** - Create and retrieve transactions
- **🛡️ Protected Routes** - Middleware-based route protection
- **📊 MongoDB Integration** - Persistent data storage

## 🛠️ Tech Stack

- **Node.js** - JavaScript runtime
- **Express.js** - Web application framework
- **MongoDB** - NoSQL database
- **Mongoose** - MongoDB ODM
- **JWT** - JSON Web Tokens for auth
- **bcrypt** - Password hashing
- **CORS** - Cross-origin resource sharing

## 🚀 Getting Started

### Prerequisites

- Node.js v16+
- MongoDB (local or Atlas)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

### Environment Variables

Create a `.env` file with the following:

```env
PORT=7000
MONGO_URI=your_mongodb_connection_string
JWT_SECRET=your_jwt_secret_key
```

### Running the Server

```bash
# Development
npm start

# Or with nodemon (if installed globally)
nodemon server.js
```

## 📂 Project Structure

```
server/
├── config/
│   └── db.js              # Database configuration
├── controllers/
│   ├── authController.js  # Auth logic
│   └── transactionController.js  # Transaction logic
├── middlewares/
│   └── authMiddleware.js  # JWT verification
├── models/
│   ├── User.js            # User model
│   └── Transaction.js     # Transaction model
├── routes/
│   ├── authRoutes.js      # Auth endpoints
│   └── transactionRoutes.js  # Transaction endpoints
├── server.js              # Entry point
└── package.json           # Dependencies
```

## 📊 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login user |
| `GET` | `/api/auth/me` | Get current user |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/transactions` | Get all user transactions |
| `POST` | `/api/transactions` | Create new transaction |
| `GET` | `/api/transactions/:id` | Get single transaction |

## 👨‍💻 Developer

**Manan Monani**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mananmonani)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/manan-monani)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/@mananmonani)
[![LeetCode](https://img.shields.io/badge/LeetCode-FFA116?style=for-the-badge&logo=leetcode&logoColor=black)](https://leetcode.com/u/mmmonani747)
[![Kaggle](https://img.shields.io/badge/Kaggle-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white)](https://www.kaggle.com/mananmonani)

📧 **Email:** [mmmonani747@gmail.com](mailto:mmmonani747@gmail.com)  
📱 **Phone:** +91 70168 53244  
📍 **Location:** Jamnagar, Gujarat, India  
🌐 **Portfolio:** Coming Soon

---

<div align="center">

Made with ❤️ by [Manan Monani](https://github.com/manan-monani)

</div>
