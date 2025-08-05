import React, { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { Eye, EyeOff, User, Mail, Lock } from "lucide-react";

const AuthForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const { login, register, loading, error, clearError } = useAuth();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    if (isLogin) {
      await login(formData.username, formData.password);
    } else {
      if (formData.password !== formData.confirmPassword) {
        alert("Passwords do not match");
        return;
      }
      await register(formData.username, formData.email, formData.password);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <div className="max-w-md w-[100vw] flex items-center justify-center  space-y-8">
        <div className="bg-red-500 grid p-8 ">
          {/* Header */}
          <div className="text-center">
            <h1 className="text-[50px] font-bold text-yellow-400 mb-2">
              PlagHunt
            </h1>
            <p className="text-gray-300 text-lg">
              Advanced Plagiarism Detection System
            </p>
          </div>

          {/* Form */}
          <div className="bg-gray-900 rounded-lg shadow-xl p-[40px] border border-gray-800">
            <div className="text-center mb-8">
              <h2 className="text-[40px] font-semibold text-yellow-400">
                {isLogin ? "Welcome Back" : "Create Account"}
              </h2>
              <p className="text-gray-400 mt-2">
                {isLogin ? "Sign in to your account" : "Join us today"}
              </p>
            </div>

            {/* Error Display */}
            {error && (
              <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded-md">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Username */}
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-medium text-yellow-400 mb-2"
                >
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-[5px] top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    id="username"
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleInputChange}
                    required
                    className="w-full h-[35px] pr-5 pl-[30px] py-3 bg-black border border-gray-700 rounded-md focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-yellow-400 placeholder-gray-500"
                    placeholder="Enter your username"
                  />
                </div>
              </div>

              {/* Email (only for register) */}
              {!isLogin && (
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-yellow-400 mb-2"
                  >
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-[5px] top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      className="w-full pl-[30px] h-[35px] pr-4 py-3 bg-black border border-gray-700 rounded-md focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-yellow-400 placeholder-gray-500"
                      placeholder="Enter your email"
                    />
                  </div>
                </div>
              )}

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-yellow-400 mb-2"
                >
                  Password
                </label>
                <div className="relative ">
                  <Lock className="absolute left-[5px] top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                    className="w-full pl-[30px] h-[35px] pr-12 py-3 bg-black border border-gray-700 rounded-md focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-yellow-400 placeholder-gray-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-yellow-400"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password (only for register) */}
              {!isLogin && (
                <div>
                  <label
                    htmlFor="confirmPassword"
                    className="block text-sm font-medium text-yellow-400 mb-2"
                  >
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-[5px] top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                    <input
                      id="confirmPassword"
                      name="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      value={formData.confirmPassword}
                      onChange={handleInputChange}
                      required
                      className="w-full pl-[30px] h-[35px] pr-4 py-3 bg-black border border-gray-700 rounded-md focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-yellow-400 placeholder-gray-500"
                      placeholder="Confirm your password"
                    />
                  </div>
                </div>
              )}
              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-yellow-500 hover:bg-yellow-600 disabled:bg-yellow-600 disabled:opacity-50 text-black font-semibold py-3 px-4 rounded-md transition duration-200 transform hover:scale-105 disabled:hover:scale-100"
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-black mr-2"></div>
                    {isLogin ? "Signing in..." : "Creating account..."}
                  </div>
                ) : isLogin ? (
                  "Sign In"
                ) : (
                  "Create Account"
                )}
              </button>
            </form>
            <br className="h-3" />

            {/* Toggle Form */}
            <div className="mt-6 text-center">
              <p className="text-gray-400">
                {isLogin
                  ? "Don't have an account?"
                  : "Already have an account?"}
                <button
                  type="button"
                  onClick={() => {
                    setIsLogin(!isLogin);
                    clearError();
                  }}
                  className="ml-2 text-yellow-400 hover:text-yellow-300 font-medium"
                >
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-gray-500 text-sm">
            <p>Secure • Fast • Reliable</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthForm;
