import React, { useState, useOptimistic } from "react";
import { useAuth } from "../../context/AuthContext";
import {
  Search,
  Github,
  LogOut,
  User,
  History,
  Loader2,
  AlertCircle,
  CheckCircle,
  Zap,
  BarChart,
  Code,
} from "lucide-react";
import AnalysisHistory from "./AnalysisHistory";
import dashboardBg from "../../assets/dashboard-bg.jpg";
import { useTransition } from "react";

const Dashboard = () => {
  const { user, logout, api } = useAuth();
  const [activeTab, setActiveTab] = useState("analyze");
  const [repoUrl, setRepoUrl] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const [optimisticAnalyses, addOptimisticAnalysis] = useOptimistic(
    [],
    (state, newAnalysis) => [...state, newAnalysis]
  );
  const [isPending, startTransition] = useTransition();

  const handleAnalysis = (e) => {
    // DEBUG 1: This is the most important log.
    // If you don't see this, your JSX onClick/onSubmit is wrong.
    console.log("handleAnalysis FUNCTION CALLED.");
    e.preventDefault();

    // DEBUG 2: Check the state value right before the condition.
    console.log("Current repoUrl value is:", repoUrl);

    if (!repoUrl) {
      console.log("EXITING: repoUrl is empty."); // Will show if the condition fails.
      setAnalysisError("Repository URL is required");
      return;
    }

    // If the logs above worked, the code will proceed.
    startTransition(async () => {
      // DEBUG 3: If you see this, the transition has started.
      console.log("INSIDE startTransition block.");
      setIsAnalyzing(true);
      setAnalysisError(null);
      setAnalysisResult(null);

      const optimisticId = Date.now().toString();
      addOptimisticAnalysis({
        id: optimisticId,
        repo_url: repoUrl,
        status: "analyzing",
        created_at: new Date().toISOString(),
      });

      // Now these will run
      console.log("Starting analysis...");

      try {
        const response = await api.post("/plagiarism/analyze", {
          repo_url: repoUrl,
          // Removed language parameter - will be auto-detected
        });
        console.log("Analysis response:", response.data);

        // Note: The optimistic state will be automatically reverted
        // when you set the final state here.
        setAnalysisResult(response.data);
      } catch (error) {
        setAnalysisError(
          error.response?.data?.error || "Analysis failed. Please try again."
        );
      } finally {
        setIsAnalyzing(false);
      }
    });
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div
      className="flex min-h-screen w-full flex-col items-center bg-slate-50 text-slate-800 dark:bg-slate-950 dark:text-slate-200 relative"
      style={{
        backgroundImage: `linear-gradient(rgba(15, 23, 42, 0.3), rgba(15, 23, 42, 0.3)), url(${dashboardBg})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        backgroundAttachment: "fixed",
      }}
    >
      {/* Header */}
      <header
        style={{
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          backdropFilter: "blur(10px)",
        }}
        className="sticky top-0 z-50 h-16 w-[100vw] border-slate-200 bg-black/60 backdrop-blur-sm dark:border-slate-800 dark:bg-slate-950/80"
      >
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-yellow-400 dark:text-yellow-400">
            PlagHunt
          </h1>

          <nav className="hidden items-center gap-2 md:flex">
            <button
              onClick={() => setActiveTab("analyze")}
              className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "analyze"
                  ? "bg-yellow-500 text-black dark:bg-yellow-500 dark:text-black"
                  : "text-yellow-300 hover:text-yellow-400 dark:text-yellow-300 dark:hover:text-yellow-400"
              }`}
            >
              <Search className="h-4 w-4" />
              Analyze
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "history"
                  ? "bg-yellow-500 text-black dark:bg-yellow-500 dark:text-black"
                  : "text-yellow-300 hover:text-yellow-400 dark:text-yellow-300 dark:hover:text-yellow-400"
              }`}
            >
              <History className="h-4 w-4" />
              History
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-yellow-300 dark:text-yellow-300">
              <User className="h-5 w-5" />
              <span>{user?.username}</span>
            </div>
            <button
              onClick={handleLogout}
              className="text-yellow-300 transition-colors hover:text-red-400 dark:hover:text-red-400"
              title="Logout"
            >
              <LogOut className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="w-[100vw] h-[20vh]"></div>
      <main className="w-[100vw] flex flex-wrap justify-center items-center max-w-4xl px-4 py-12 sm:px-6 sm:py-16 lg:px-8 ">
        {activeTab === "analyze" && (
          <div
            className="space-y-12 rounded-[20px] p-[20px] w-[69%]"
            style={{
              backgroundColor: "rgba(0, 0, 0, 0.5)",
              backdropFilter: "blur(10px)",
            }}
          >
            {/* Hero Section */}
            <div className="text-center">
              <h2 className="text-4xl font-extrabold text-yellow-400 dark:text-yellow-400 sm:text-5xl">
                Detect Code Plagiarism
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-300 dark:text-gray-300">
                Enter a GitHub repository URL and we'll automatically detect the
                programming languages and analyze for potential plagiarism.
              </p>
            </div>

            {/* Form Container */}
            <div
              className="rounded-xl p-6 shadow-lg sm:p-8 bg-black bg-opacity-90"
              // style={{
              //   backgroundColor: "black",
              //   background: "black",
              // }}
            >
              <form onSubmit={handleAnalysis} className="space-y-6">
                <div>
                  <label
                    htmlFor="repoUrl"
                    className="mb-2 block text-sm font-medium text-yellow-300 dark:text-yellow-300"
                  >
                    GitHub Repository URL
                  </label>
                  <div className="relative flex flex-wrap justify-center items-center my-[20px]">
                    <div className="w-[50%] relative">
                      <Github
                        className="pointer-events-none absolute left-[7px] top-1/2 h-[30px] w-[30px] -translate-y-1/2 text-gray-400"
                        aria-hidden="true"
                      />
                      <input
                        id="repoUrl"
                        type="url"
                        value={repoUrl}
                        onChange={(e) => setRepoUrl(e.target.value)}
                        placeholder="https://github.com/username/repository"
                        className="rounded-lg w-full h-[60px] pl-[40px] border border-gray-600 rounded-[20px] text-[25px] bg-black/50 py-2.5 pr-4 text-yellow-300 placeholder:text-gray-400 focus:border-yellow-400 focus:outline-none focus:ring-2 focus:ring-yellow-400/20 dark:border-gray-600 dark:text-yellow-300 dark:focus:border-yellow-400"
                      />
                    </div>
                  </div>
                </div>

                {/* Replace language selection with info text */}
                {/* <div className="text-center">
                  <p className="text-sm text-gray-400 mb-4">
                    <Code className="inline h-4 w-4 mr-1" />
                    <strong>Smart Language Detection:</strong> We'll automatically detect Python, JavaScript, TypeScript, Java, C++, Rust, Solidity, and 20+ other programming languages in your repository for accurate analysis.
                  </p>
                </div> */}

                <button
                  type="submit"
                  disabled={isAnalyzing}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-yellow-500 py-3 px-4 font-semibold text-black transition-colors hover:bg-yellow-600 active:bg-yellow-700 disabled:cursor-not-allowed disabled:bg-yellow-400 dark:disabled:bg-yellow-600"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Analyzing Repository...
                    </>
                  ) : (
                    <>
                      <Search className="h-5 w-5" />
                      Start Smart Analysis
                    </>
                  )}
                </button>
              </form>

              {analysisError && (
                <div className="mt-6 flex items-center gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-400">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <p>{analysisError}</p>
                </div>
              )}

              {analysisResult && (
                <div className="mt-6 space-y-6">
                  {/* Header */}
                  <div className="flex items-center gap-3 rounded-lg border border-green-500/30 bg-green-500/10 p-4 font-medium text-green-700 dark:text-green-400">
                    <CheckCircle className="h-5 w-5" />
                    Analysis Complete!
                  </div>

                  {/* Analysis Outcome Section */}
                  <div className="rounded-lg border border-gray-600 bg-black/70 p-6">
                    <div className="mb-4 flex items-center gap-2">
                      <BarChart className="h-5 w-5 text-yellow-400" />
                      <h3 className="text-lg font-semibold text-yellow-400">
                        Analysis Outcome
                      </h3>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-3">
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            Total Repositories Compared
                          </span>
                          <span className="text-white font-medium">
                            {analysisResult.summary?.total_candidates_checked ||
                              0}
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            Highest Overall Similarity
                          </span>
                          <span className="text-white font-medium">
                            {(
                              analysisResult.summary?.highest_similarity || 0
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            Highest Code Similarity
                          </span>
                          <span className="text-white font-medium">
                            {(
                              analysisResult.summary?.max_code_similarity || 0
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            Highest Structure Similarity
                          </span>
                          <span className="text-white font-medium">
                            {(
                              analysisResult.summary
                                ?.max_structure_similarity || 0
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                      </div>

                      <div className="space-y-3">
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            README Similarity
                          </span>
                          <span className="text-white font-medium">
                            {(
                              analysisResult.summary?.max_readme_similarity || 0
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            Plagiarism Detected
                          </span>
                          <span
                            className={`font-medium flex items-center gap-1 ${
                              analysisResult.plagiarism_detected
                                ? "text-red-400"
                                : "text-green-400"
                            }`}
                          >
                            {analysisResult.plagiarism_detected ? "⚠" : "✓"}{" "}
                            {analysisResult.plagiarism_detected ? "Yes" : "No"}
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">Risk Level</span>
                          <span
                            className={`font-medium flex items-center gap-1 ${
                              analysisResult.summary?.overall_risk_level ===
                              "Low"
                                ? "text-green-400"
                                : analysisResult.summary?.overall_risk_level ===
                                  "Medium"
                                ? "text-yellow-400"
                                : "text-red-400"
                            }`}
                          >
                            {analysisResult.summary?.overall_risk_level ===
                            "Low"
                              ? "✓"
                              : analysisResult.summary?.overall_risk_level ===
                                "Medium"
                              ? "⚠"
                              : "⚠"}{" "}
                            {analysisResult.summary?.overall_risk_level ||
                              "Low"}
                          </span>
                        </div>
                        <div className="flex justify-between py-2 border-b border-gray-700">
                          <span className="text-gray-300">
                            High Similarity Repos Found
                          </span>
                          <span className="text-white font-medium">
                            {analysisResult.summary?.high_similarity_count || 0}
                          </span>
                        </div>
                        <div className="flex justify-between py-2">
                          <span className="text-gray-300">
                            Average Similarity Score
                          </span>
                          <span className="text-white font-medium">
                            {(
                              analysisResult.summary?.average_similarity || 0
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Language Detection Results */}
                  {analysisResult.suspect_repo?.primary_languages && (
                    <div className="rounded-lg border border-blue-600 bg-blue-500/10 p-6">
                      <div className="mb-4 flex items-center gap-2">
                        <Code className="h-5 w-5 text-blue-400" />
                        <h3 className="text-lg font-semibold text-blue-400">
                          Detected Languages
                        </h3>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-gray-300 mb-2">
                            <strong>Primary Languages:</strong>
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {analysisResult.suspect_repo?.primary_languages?.map(
                              (lang, index) => (
                                <span
                                  key={index}
                                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                                    index === 0
                                      ? "bg-blue-500/30 text-blue-300 border border-blue-400"
                                      : "bg-blue-500/20 text-blue-400"
                                  }`}
                                >
                                  {lang} {index === 0 && "(Primary)"}
                                </span>
                              )
                            )}
                          </div>
                        </div>

                        <div>
                          <p className="text-gray-300 mb-2">
                            <strong>Language Breakdown:</strong>
                          </p>
                          <div className="space-y-1">
                            {analysisResult.suspect_repo?.language_breakdown
                              ?.slice(0, 4)
                              .map((lang, index) => (
                                <div
                                  key={index}
                                  className="flex justify-between text-sm"
                                >
                                  <span className="text-gray-300">
                                    {lang.language}
                                  </span>
                                  <span className="text-blue-400">
                                    {lang.percentage}% ({lang.file_count} files)
                                  </span>
                                </div>
                              ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Project Uniqueness Assessment */}
                  {analysisResult.uniqueness_assessment && (
                    <div className="rounded-lg border border-gray-600 bg-black/70 p-6">
                      <div className="mb-4 flex items-center gap-2">
                        <BarChart className="h-5 w-5 text-blue-400" />
                        <h3 className="text-lg font-semibold text-blue-400">
                          Project Uniqueness Assessment
                        </h3>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                          <div className="flex justify-between py-2 border-b border-gray-700">
                            <span className="text-gray-300">
                              Overall Uniqueness
                            </span>
                            <span className="text-white font-medium">
                              {
                                analysisResult.uniqueness_assessment
                                  .overall_uniqueness
                              }
                              %
                            </span>
                          </div>
                          <div className="flex justify-between py-2 border-b border-gray-700">
                            <span className="text-gray-300">
                              Topic Uniqueness
                            </span>
                            <span className="text-white font-medium">
                              {
                                analysisResult.uniqueness_assessment
                                  .topic_uniqueness
                              }
                              %
                            </span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-gray-300">
                              Keyword Uniqueness
                            </span>
                            <span className="text-white font-medium">
                              {
                                analysisResult.uniqueness_assessment
                                  .keyword_uniqueness
                              }
                              %
                            </span>
                          </div>
                        </div>

                        <div className="space-y-3">
                          <div className="flex justify-between py-2 border-b border-gray-700">
                            <span className="text-gray-300">Project Type</span>
                            <span
                              className={`font-medium flex items-center gap-1 ${
                                analysisResult.uniqueness_assessment
                                  .is_advanced_project_type
                                  ? "text-green-400"
                                  : analysisResult.uniqueness_assessment
                                      .is_common_project_type
                                  ? "text-yellow-400"
                                  : "text-blue-400"
                              }`}
                            >
                              {analysisResult.uniqueness_assessment
                                .is_advanced_project_type
                                ? "✓ Advanced"
                                : analysisResult.uniqueness_assessment
                                    .is_common_project_type
                                ? "⚠ Common"
                                : "○ Standard"}
                            </span>
                          </div>
                          <div className="flex justify-between py-2 border-b border-gray-700">
                            <span className="text-gray-300">
                              Keyword Overlap with Candidates
                            </span>
                            <span className="text-white font-medium">
                              {
                                analysisResult.uniqueness_assessment
                                  .avg_keyword_overlap
                              }
                              %
                            </span>
                          </div>
                          <div className="flex justify-between py-2">
                            <span className="text-gray-300">
                              Originality Score
                            </span>
                            <span
                              className={`font-medium ${
                                analysisResult.uniqueness_assessment
                                  .overall_uniqueness > 70
                                  ? "text-green-400"
                                  : analysisResult.uniqueness_assessment
                                      .overall_uniqueness > 50
                                  ? "text-yellow-400"
                                  : "text-red-400"
                              }`}
                            >
                              {analysisResult.uniqueness_assessment
                                .overall_uniqueness > 70
                                ? "High"
                                : analysisResult.uniqueness_assessment
                                    .overall_uniqueness > 50
                                ? "Medium"
                                : "Low"}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Repository Details */}
                  <div className="rounded-lg border border-gray-600 bg-black/70 p-6">
                    <h3 className="text-lg font-semibold text-yellow-400 mb-4">
                      Repository Details
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-gray-300 mb-2">
                          <strong>Repository:</strong>{" "}
                          {analysisResult.suspect_repo?.name || "N/A"}
                        </p>
                        <p className="text-gray-300 mb-2">
                          <strong>Owner:</strong>{" "}
                          {analysisResult.suspect_repo?.owner || "N/A"}
                        </p>
                        <p className="text-gray-300 mb-2">
                          <strong>Topic:</strong>{" "}
                          {analysisResult.suspect_repo?.topic || "N/A"}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-300 mb-2">
                          <strong>URL:</strong>
                          <a
                            href={analysisResult.suspect_repo?.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-yellow-400 hover:text-yellow-300 ml-1"
                          >
                            {analysisResult.suspect_repo?.url}
                          </a>
                        </p>
                        <p className="text-gray-300 mb-2">
                          <strong>Result ID:</strong> {analysisResult.result_id}
                        </p>
                        <p className="text-gray-300 mb-2">
                          <strong>Status:</strong>
                          <span className="text-green-400 ml-1 capitalize">
                            {analysisResult.status}
                          </span>
                        </p>
                      </div>
                    </div>

                    {/* Keywords */}
                    {analysisResult.suspect_repo?.keywords &&
                      analysisResult.suspect_repo.keywords.length > 0 && (
                        <div className="mt-4">
                          <p className="text-gray-300 mb-2">
                            <strong>Keywords:</strong>
                          </p>
                          <div className="flex flex-wrap gap-2">
                            {analysisResult.suspect_repo.keywords.map(
                              (keyword, index) => (
                                <span
                                  key={index}
                                  className="px-2 py-1 bg-yellow-500/20 text-yellow-300 rounded text-sm"
                                >
                                  {keyword}
                                </span>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>

                  {/* Candidate Repositories */}
                  {analysisResult.analysis_results &&
                    analysisResult.analysis_results.length > 0 && (
                      <div className="rounded-lg border border-gray-600 bg-black/70 p-6">
                        <h3 className="text-lg font-semibold text-yellow-400 mb-4">
                          Similar Repositories Found
                        </h3>
                        <div className="space-y-4 max-h-96 overflow-y-auto">
                          {analysisResult.analysis_results.map(
                            (result, index) => (
                              <div
                                key={index}
                                className="border border-gray-700 rounded-lg p-4"
                              >
                                <div className="flex justify-between items-start mb-2">
                                  <div>
                                    <h4 className="text-white font-medium">
                                      <a
                                        href={result.candidate_repo.url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-yellow-400 hover:text-yellow-300"
                                      >
                                        {result.candidate_repo.name}
                                      </a>
                                    </h4>
                                    <p className="text-gray-400 text-sm">
                                      {result.candidate_repo.language} • ⭐{" "}
                                      {result.candidate_repo.stars}
                                    </p>
                                  </div>
                                  <div className="flex flex-col gap-1">
                                    <span
                                      className={`px-2 py-1 rounded text-xs font-medium ${
                                        result.risk_assessment?.risk_level ===
                                        "Critical"
                                          ? "bg-red-600/30 text-red-300"
                                          : result.risk_assessment
                                              ?.risk_level === "High"
                                          ? "bg-red-500/20 text-red-400"
                                          : result.risk_assessment
                                              ?.risk_level === "Medium"
                                          ? "bg-yellow-500/20 text-yellow-400"
                                          : "bg-green-500/20 text-green-400"
                                      }`}
                                    >
                                      {result.risk_assessment?.risk_level ||
                                        "Low"}{" "}
                                      Risk
                                    </span>
                                  </div>
                                </div>

                                <p className="text-gray-300 text-sm mb-3 line-clamp-2">
                                  {result.candidate_repo.description}
                                </p>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                                  <div className="text-center">
                                    <div className="text-yellow-400 font-medium">
                                      {result.similarity_scores.overall_similarity.toFixed(
                                        1
                                      )}
                                      %
                                    </div>
                                    <div className="text-gray-400">Overall</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-blue-400 font-medium">
                                      {result.similarity_scores.code_similarity.toFixed(
                                        1
                                      )}
                                      %
                                    </div>
                                    <div className="text-gray-400">Code</div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-green-400 font-medium">
                                      {result.similarity_scores.structure_similarity.toFixed(
                                        1
                                      )}
                                      %
                                    </div>
                                    <div className="text-gray-400">
                                      Structure
                                    </div>
                                  </div>
                                  <div className="text-center">
                                    <div className="text-purple-400 font-medium">
                                      {result.similarity_scores.readme_similarity.toFixed(
                                        1
                                      )}
                                      %
                                    </div>
                                    <div className="text-gray-400">README</div>
                                  </div>
                                </div>

                                {result.overlap_files &&
                                  result.overlap_files.length > 0 && (
                                    <div className="mt-2">
                                      <p className="text-gray-400 text-xs">
                                        Overlapping files:{" "}
                                        {result.overlap_files.length}
                                      </p>
                                    </div>
                                  )}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </div>

            {/* Features Section */}
            <div className="grid grid-cols-1 gap-6 text-center md:grid-cols-3">
              <div className="space-y-2">
                <Zap className="mx-auto h-8 w-8 text-yellow-400 dark:text-yellow-400" />
                <h3 className="text-lg font-semibold text-yellow-300 dark:text-yellow-300">
                  Fast Results
                </h3>
                <p className="text-gray-300 dark:text-gray-300">
                  Get comprehensive plagiarism reports in minutes.
                </p>
              </div>
              <div className="space-y-2">
                <Search className="mx-auto h-8 w-8 text-yellow-400 dark:text-yellow-400" />
                <h3 className="text-lg font-semibold text-yellow-300 dark:text-yellow-300">
                  Deep Analysis
                </h3>
                <p className="text-gray-300 dark:text-gray-300">
                  Advanced algorithms analyze code structure and patterns.
                </p>
              </div>
              <div className="space-y-2">
                <BarChart className="mx-auto h-8 w-8 text-yellow-400 dark:text-yellow-400" />
                <h3 className="text-lg font-semibold text-yellow-300 dark:text-yellow-300">
                  Detailed Reports
                </h3>
                <p className="text-gray-300 dark:text-gray-300">
                  Visual similarity scores and line-by-line comparisons.
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === "history" && (
          <AnalysisHistory optimisticAnalyses={optimisticAnalyses} />
        )}
      </main>
    </div>
  );
};

export default Dashboard;
