export const Home = () => {
    return (
        <div className="flex justify-center items-center min-h-screen bg-gray-100 px-4">
            <div className="max-w-3xl text-center p-8 bg-white shadow-lg rounded-xl">
                <h1 className="text-3xl font-bold mb-4 text-gray-800">
                    Welcome to the Fraud Detection System: <span className="text-blue-600">Defraudo</span>
                </h1>
                <h2 className="text-xl font-semibold mb-4 text-gray-700">
                    This project aims to develop an AI-powered fraud detection system for digital transactions.
                </h2>
                <p className="text-lg text-gray-600 text-justify leading-relaxed">
                    The system uses a machine learning model to analyze transactions in real-time and identify fraudulent activities. 
                    The backend is built with Node.js, while the frontend is implemented using React Native. 
                    The fraud detection model and API are managed by our team members, with other tasks divided among the remaining team members.
                </p>
            </div>
        </div>
    );
};
