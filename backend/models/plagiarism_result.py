from models.database import db
from datetime import datetime
from bson.objectid import ObjectId

class PlagiarismResult:
    def __init__(self):
        self.collection = db.get_collection('plagiarism_results')
    
    def save_result(self, user_id, repo_url, analysis_data):
        """Save plagiarism analysis result"""
        result_data = {
            "user_id": user_id,
            "repo_url": repo_url,
            "analysis_data": analysis_data,
            "created_at": datetime.utcnow(),
            "status": "completed"
        }
        
        result = self.collection.insert_one(result_data)
        return str(result.inserted_id)
    
    def get_user_history(self, user_id, limit=50, skip=0):
        """Get user's plagiarism analysis history"""
        try:
            results = self.collection.find(
                {"user_id": user_id}
            ).sort("created_at", -1).limit(limit).skip(skip)
            
            history = []
            for result in results:
                result['_id'] = str(result['_id'])
                history.append(result)
            
            return history
        except Exception as e:
            print(f"Error fetching user history: {e}")
            return []
    
    def get_result_by_id(self, result_id):
        """Get specific plagiarism result by ID"""
        try:
            result = self.collection.find_one({"_id": ObjectId(result_id)})
            if result:
                result['_id'] = str(result['_id'])
                return result
            return None
        except:
            return None
    
    def delete_result(self, result_id, user_id):
        """Delete a plagiarism result (only by owner)"""
        try:
            result = self.collection.delete_one({
                "_id": ObjectId(result_id),
                "user_id": user_id
            })
            return result.deleted_count > 0
        except:
            return False
    
    def get_stats(self, user_id):
        """Get user statistics"""
        try:
            total_analyses = self.collection.count_documents({"user_id": user_id})
            
            # Get recent analyses (last 30 days)
            thirty_days_ago = datetime.utcnow().replace(day=datetime.utcnow().day - 30)
            recent_analyses = self.collection.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            })
            
            return {
                "total_analyses": total_analyses,
                "recent_analyses": recent_analyses
            }
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"total_analyses": 0, "recent_analyses": 0}
