import { createContext } from "react";

const AuthContext = createContext();
const AuthProvider = ({ children }) => {

    const storetokenInsessionStorage = (serverToken) => {
        return sessionStorage.setItem("token", serverToken);
    };
    return <AuthContext.Provider value={{storetokenInsessionStorage}}>{children}</AuthContext.Provider>;
}
export default AuthContext;
