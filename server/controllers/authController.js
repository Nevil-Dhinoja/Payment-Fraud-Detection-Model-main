const User = require('../models/User');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

exports.register = async (req, res) => {
    const { username, password, email, phone } = req.body;

    // Validate input fields
    if (!username || !password || !email || !phone) {
        return res.status(400).json({ message: 'All fields (username, password, email, phone) are required' });
    }

    try {
        // Check if email or phone already exists
        const existingUser = await User.findOne({ $or: [{ email }, { phone }] });
        if (existingUser) {
            return res.status(400).json({ message: 'Email or phone number already in use' });
        }

        // Hash the password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Create a new user
        const newUser = new User({ username, password: hashedPassword, email, phone });
        await newUser.save();

        // Generate JWT token (expires in 30 minutes)
        const token = jwt.sign(
            { _id: newUser._id, email: newUser.email, username: newUser.username },
            process.env.JWT_SECRET,
            { expiresIn: '30m' }
        );

        res.status(201).json({
            message: 'User registered and logged in successfully',
            token,
        });
    } catch (err) {
        res.status(500).json({ message: 'Error registering user', error: err.message });
    }
};

exports.login = async (req, res) => {
    const { identifier, password } = req.body;

    // Validate input
    if (!identifier || !password) {
        return res.status(400).json({ message: 'Email/Phone and password are required' });
    }

    try {
        // Find user by email or phone
        const user = await User.findOne({
            $or: [{ email: identifier }, { phone: identifier }]
        });

        if (!user) {
            return res.status(400).json({ message: 'User not found' });
        }

        // Compare password
        const validPassword = await bcrypt.compare(password, user.password);
        if (!validPassword) {
            return res.status(400).json({ message: 'Invalid password' });
        }

        // Generate JWT token (expires in 30 minutes)
        const token = jwt.sign(
            { _id: user._id, email: user.email, username: user.username },
            process.env.JWT_SECRET,
            { expiresIn: '30m' }
        );

        // Send response with token
        res.header('Authorization', token).json({ message: 'Logged in successfully', token });
    } catch (error) {
        res.status(500).json({ message: 'Error logging in', error: error.message });
    }
};
