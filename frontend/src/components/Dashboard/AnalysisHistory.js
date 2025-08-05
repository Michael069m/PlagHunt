import React, { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  Calendar,
  ExternalLink,
  Trash2,
  Eye,
  Clock,
  BarChart3,
  Github,
} from "lucide-react";

const AnalysisHistory = () => {
  const { api } = useAuth();
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState({ total_analyses: 0, recent_analyses: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedResult, setSelectedResult] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get("/plagiarism/history");
        const data = response.data;
        setHistory(data.history || []);
        setStats(data.stats || { total_analyses: 0, recent_analyses: 0 });
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [api]);

  const handleDelete = async (resultId) => {
    if (!confirm("Are you sure you want to delete this analysis?")) return;

    try {
      await api.delete(`/plagiarism/result/${resultId}`);
      setHistory(history.filter((item) => item._id !== resultId));
      setStats((prev) => ({
        ...prev,
        total_analyses: Math.max(0, prev.total_analyses - 1),
      }));
    } catch (error) {
      console.error("Error deleting result:", error);
      alert("Failed to delete analysis. Please try again.");
    }
  };

  const handleViewDetails = async (resultId) => {
    try {
      const response = await api.get(`/plagiarism/result/${resultId}`);
      setSelectedResult(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error("Error fetching result details:", error);
      alert("Failed to load analysis details.");
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getRepoName = (url) => {
    try {
      const parts = url.split("/");
      return `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
    } catch {
      return url;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 w-full bg-red-100">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <BarChart3 className="h-8 w-8 text-yellow-400 mr-3" />
            <div>
              <p className="text-sm text-gray-400">Total Analyses</p>
              <p className="text-2xl font-bold text-yellow-400">
                {stats.total_analyses}
              </p>
            </div>
          </div>
        </div>
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-yellow-400 mr-3" />
            <div>
              <p className="text-sm text-gray-400">Recent (30 days)</p>
              <p className="text-2xl font-bold text-yellow-400">
                {stats.recent_analyses}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* History Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-yellow-400">Analysis History</h2>
        <p className="text-gray-400">{history.length} total results</p>
      </div>

      {/* History List */}
      {history.length === 0 ? (
        <div className="text-center py-12">
          <Github className="h-16 w-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-400 mb-2">
            No analyses yet
          </h3>
          <p className="text-gray-500">
            Start by analyzing your first repository!
          </p>
        </div>
      ) : (
        <div className="bg-gray-900 rounded-lg border border-gray-800 overflow-hidden">
          <div className="divide-y divide-gray-800">
            {history.map((item) => (
              <div
                key={item._id}
                className="p-6 hover:bg-gray-800 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3">
                      <Github className="h-5 w-5 text-gray-400" />
                      <h3 className="text-lg font-medium text-yellow-400 truncate">
                        {getRepoName(item.repo_url)}
                      </h3>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          item.status === "completed"
                            ? "bg-green-900 text-green-400"
                            : "bg-yellow-900 text-yellow-400"
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <div className="mt-2 flex items-center text-sm text-gray-400 space-x-4">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(item.created_at)}
                      </div>
                      {item.analysis_data?.language && (
                        <div>
                          Language:{" "}
                          <span className="text-yellow-400">
                            {item.analysis_data.language}
                          </span>
                        </div>
                      )}
                      {item.analysis_data?.candidates_analyzed && (
                        <div>
                          Candidates:{" "}
                          <span className="text-yellow-400">
                            {item.analysis_data.candidates_analyzed}
                          </span>
                        </div>
                      )}
                    </div>
                    <p className="mt-1 text-sm text-gray-500 truncate">
                      {item.repo_url}
                    </p>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => handleViewDetails(item._id)}
                      className="inline-flex items-center px-3 py-1.5 border border-yellow-500 text-sm font-medium rounded-md text-yellow-400 hover:bg-yellow-500 hover:text-black transition-colors"
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </button>
                    <a
                      href={item.repo_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-3 py-1.5 border border-gray-600 text-sm font-medium rounded-md text-gray-400 hover:bg-gray-700 transition-colors"
                    >
                      <ExternalLink className="h-4 w-4 mr-1" />
                      GitHub
                    </a>
                    <button
                      onClick={() => handleDelete(item._id)}
                      className="inline-flex items-center px-3 py-1.5 border border-red-600 text-sm font-medium rounded-md text-red-400 hover:bg-red-600 hover:text-white transition-colors"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {showDetailModal && selectedResult && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-900 rounded-lg border border-gray-800 max-w-4xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-yellow-400">
                  Analysis Details
                </h3>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-400 hover:text-yellow-400"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-6">
                <div>
                  <h4 className="text-lg font-medium text-yellow-400 mb-2">
                    Repository Information
                  </h4>
                  <div className="bg-black p-4 rounded border border-gray-700">
                    <p className="text-gray-300">
                      <span className="font-medium">URL:</span>{" "}
                      {selectedResult.repo_url}
                    </p>
                    <p className="text-gray-300">
                      <span className="font-medium">Analyzed:</span>{" "}
                      {formatDate(selectedResult.created_at)}
                    </p>
                    {selectedResult.analysis_data?.language && (
                      <p className="text-gray-300">
                        <span className="font-medium">Language:</span>{" "}
                        {selectedResult.analysis_data.language}
                      </p>
                    )}
                  </div>
                </div>

                {selectedResult.analysis_data?.analysis_results && (
                  <div>
                    <h4 className="text-lg font-medium text-yellow-400 mb-2">
                      Analysis Results
                    </h4>
                    <div className="bg-black p-4 rounded border border-gray-700">
                      <pre className="text-gray-300 text-sm whitespace-pre-wrap overflow-x-auto">
                        {JSON.stringify(
                          selectedResult.analysis_data.analysis_results,
                          null,
                          2
                        )}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisHistory;
