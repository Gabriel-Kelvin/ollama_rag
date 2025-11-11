# Bug Fixes Applied ✅

## Issues Fixed

### 1. ✅ Document Count Shows Correct Number
**Problem**: Knowledge bases always showed "0 documents" even when files were uploaded.

**Fix**: Updated the backend `/knowledge-bases` endpoint to actually count the files in each KB.

**Location**: `backend/main.py` - `list_knowledge_bases()` function

### 2. ✅ Knowledge Base Permanent Deletion
**Problem**: Deleted KBs reappeared after page reload.

**Fix**: 
- Frontend now immediately removes the KB from the UI state
- Backend improved to delete all data (vector store, uploads folder, chunks folder)
- Added better logging to track deletion process

**Locations**: 
- `web/src/pages/app/KnowledgeBasesPage.tsx` - `handleDelete()` function
- `backend/main.py` - `delete_knowledge_base()` function

## How to Test

### Testing Document Count

1. **Restart the backend** (the changes are in backend code):
   ```bash
   # Stop the backend (Ctrl+C)
   # Then restart:
   uvicorn backend.main:app --reload --port 8000
   ```

2. Go to Knowledge Bases page
3. Create or select a KB
4. Upload a document
5. Go back to Knowledge Bases page
6. **You should now see "1 document"** instead of "0 documents"

### Testing KB Deletion

1. **No need to restart** (frontend changes hot-reload automatically)

2. Create a test knowledge base (e.g., "Test KB")

3. Upload a document to it

4. Click the delete button (trash icon)

5. Confirm deletion

6. **Immediate result**: KB should disappear from the list immediately

7. **Refresh the page** (F5 or Ctrl+R)

8. **Expected**: The KB should still be gone (not reappear)

9. **Check backend logs**: You should see detailed deletion logs like:
   ```
   🗑️ Deleting knowledge base: Test KB for user xxx@example.com
      ✓ Deleted collection from vector store: Test KB
      ✓ Deleted directory: data/uploads/Test KB
      ✓ Deleted chunks directory: data/chunks/Test KB
   ✓ Successfully deleted knowledge base: Test KB
   ```

## Verification Checklist

- [ ] Backend restarted with new code
- [ ] Document count shows correct number (not 0)
- [ ] Deleted KB disappears immediately
- [ ] Deleted KB stays gone after page refresh
- [ ] Backend logs show successful deletion

## What the Fixes Do

### Document Count Fix
```python
# Before: Hardcoded to 0
kbs = [{"name": kb_name, "created_at": None, "doc_count": 0} for kb_name in kb_list]

# After: Actually counts files
for kb_name in kb_list:
    files = list_kb_files(kb_name)
    doc_count = len(files)
    kbs.append({"name": kb_name, "created_at": None, "doc_count": doc_count})
```

### Deletion Fix

**Frontend**:
```typescript
// Immediately remove from UI
setKbs((prevKbs) => prevKbs.filter((kb) => kb.name !== name));

// Then refresh from server to ensure consistency
setTimeout(() => {
  fetchKbs();
}, 500);
```

**Backend**:
```python
# Delete from vector store
vector_store.delete_kb(kb_name)

# Delete uploads directory
shutil.rmtree(Path("data/uploads") / kb_name)

# Delete chunks directory
shutil.rmtree(Path("data/chunks") / kb_name)
```

## Additional Improvements

1. **Better error messages**: Delete errors now show specific details
2. **Confirmation dialog**: Now mentions that documents will also be deleted
3. **Logging**: Backend now logs each deletion step for debugging
4. **Robustness**: Backend continues even if vector store deletion fails

## If Issues Persist

### Document Count Still Shows 0
1. Check if files are actually in `data/uploads/{kb_name}/`
2. Check backend logs for errors
3. Try creating a new KB and uploading to it

### KB Still Reappears After Deletion
1. Check backend logs for deletion errors
2. Verify vector database is running (Qdrant/ChromaDB)
3. Check if `data/uploads/{kb_name}` folder is actually deleted
4. Try manually deleting the folder and refreshing

### Debug Mode
To see detailed logs, check your backend terminal. You should see:
- `🗑️ Deleting knowledge base: {name}`
- `✓ Deleted collection from vector store`
- `✓ Deleted directory: ...`
- `✓ Successfully deleted knowledge base`

If you see `⚠️ Error deleting from vector store`, there might be an issue with your vector database connection.

## Summary

Both issues are now fixed! 
- ✅ Document counts are accurate
- ✅ Deletions are permanent

Just restart your backend to apply the changes, and everything should work perfectly.

