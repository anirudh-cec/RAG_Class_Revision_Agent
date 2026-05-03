# Frontend Implementation Specification

## Document Information
- **Based on**: `.claude/plans/01.Frontend_implementation_plan.md`
- **Target Location**: `frontend/` folder
- **Framework**: Streamlit
- **Version**: 1.0.0

---

## 1. Project Structure

```
frontend/
├── app.py                      # Main entry point
├── requirements.txt            # Python dependencies
├── .streamlit/
│   └── config.toml            # Streamlit theme configuration
├── components/
│   ├── __init__.py
│   ├── step_indicator.py      # Progress/step indicator component
│   ├── file_uploader.py       # Custom file upload wrapper
│   ├── github_input.py        # GitHub URL input component
│   └── review_card.py         # Review page card component
├── styles/
│   ├── __init__.py
│   └── custom_css.py          # CSS injection utilities
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Input validation functions
│   ├── file_handler.py        # File saving operations
│   └── session_state.py       # Session state management
└── pages/
    ├── __init__.py
    ├── landing.py             # Step 0: Landing page
    ├── vtt_upload.py          # Step 1: VTT upload
    ├── code_upload.py         # Step 2: Code files upload
    ├── github_upload.py       # Step 3: GitHub links
    ├── review.py              # Step 4: Review page
    └── success.py             # Step 5: Success page
```

---

## 2. File Specifications

### 2.1 Main Entry Point (`app.py`)

**Purpose**: Central router that manages the application flow based on session state.

**Key Functions**:
- `initialize_session_state()`: Sets up all required session state variables
- `main()`: Main render loop that routes to the appropriate page based on `current_step`

**Session State Variables**:
```python
{
    "current_step": int,  # 0-5
    "vtt_files": list,  # UploadedFile objects
    "code_files": list,  # UploadedFile objects  
    "github_urls": list,  # strings
    "has_code_files": bool | None,
    "has_github_repos": bool | None,
    "processing": bool,
    "completed": bool,
    "errors": list,
    "docs_path": str  # Path to docs folder
}
```

---

### 2.2 Components

#### 2.2.1 `step_indicator.py`

**Function**: `render_step_indicator(current_step: int, steps: list[str])`

**Visual Design**:
- Horizontal progress bar with 6 steps
- Completed steps: Green with checkmark icon
- Current step: Blue with pulse animation
- Future steps: Gray
- Step labels below each indicator

**Steps Array**:
```python
["Start", "VTT Files", "Code Files", "GitHub", "Review", "Done"]
```

---

#### 2.2.2 `file_uploader.py`

**Functions**:
- `render_vtt_uploader() -> list[UploadedFile]`
- `render_code_uploader() -> list[UploadedFile]`

**Features**:
- Drag-and-drop zone with file type icons
- Multiple file selection
- File list with remove buttons
- Validation messages (file type, size)
- Preview capability for first file

---

#### 2.2.3 `github_input.py`

**Function**: `render_github_inputs() -> list[str]`

**Features**:
- Dynamic URL input fields
- "Add Another Repository" button
- URL validation with visual feedback (green check / red X)
- Remove button for each URL
- Summary count of valid URLs
- Optional branch selector per repo (default: main/master)

**Validation Rules**:
- Must start with `https://github.com/`
- Must have format: `github.com/{owner}/{repo}`
- No trailing slash (normalized)

---

#### 2.2.4 `review_card.py`

**Function**: `render_review_card(title: str, items: list, icon: str)`

**Card Types**:
1. **VTT Files Card**: Green header, file count, expandable file list
2. **Code Files Card**: Blue header, file count + languages, expandable list
3. **GitHub Repos Card**: Purple header, repo count, branch info, expandable list

**Actions**:
- Edit link per card (navigates back to that step)
- Expand/collapse for long lists

---

### 2.3 Styles (`custom_css.py`)

**Function**: `inject_custom_css()`

**CSS Sections**:

1. **Global Styles**
   - Font family: Inter or system-ui
   - Background color: #f8fafc
   - Text color: #1e293b

2. **Header Styles**
   - Gradient background (blue to indigo)
   - White text, centered
   - Padding and border radius

3. **Card Styles**
   - White background
   - Box shadow: 0 1px 3px rgba(0,0,0,0.1)
   - Border radius: 8px
   - Padding: 24px

4. **Button Styles**
   - Primary: Blue background, white text
   - Secondary: Gray background, dark text
   - Danger: Red background (for remove actions)
   - Hover states with darker shades

5. **Step Indicator Styles**
   - Circle indicators with numbers/icons
   - Completed: Green with checkmark
   - Current: Blue with pulse
   - Future: Gray
   - Connecting lines between steps

6. **Form Styles**
   - Input fields with focus rings
   - Validation states (green border for valid, red for invalid)
   - Help text styling

7. **Animation Styles**
   - Pulse animation for current step
   - Fade-in for cards
   - Spinner animation for loading states

---

### 2.4 Utils

#### 2.4.1 `validators.py`

**Functions**:
- `validate_vtt_file(file) -> tuple[bool, str]`
  - Check file extension is .vtt
  - Check file size < 50MB
  - Return (is_valid, error_message)

- `validate_code_file(file) -> tuple[bool, str]`
  - Check extension against allowed list
  - Check file size < 10MB per file
  - Return (is_valid, error_message)

- `validate_github_url(url: str) -> tuple[bool, str, dict]`
  - Check URL starts with https://github.com/
  - Parse owner and repo name
  - Normalize URL (remove trailing slash, .git)
  - Return (is_valid, error_message, parsed_data)

#### 2.4.2 `file_handler.py`

**Functions**:
- `ensure_docs_folder() -> str`
  - Create docs/ folder if it doesn't exist
  - Create subfolders: vtt/, code/, github/
  - Return path to docs folder

- `save_vtt_files(files: list, docs_path: str) -> list[str]`
  - Save each VTT file to docs/vtt/
  - Return list of saved file paths

- `save_code_files(files: list, docs_path: str) -> list[str]`
  - Save each code file to docs/code/
  - Maintain original filenames
  - Return list of saved file paths

- `fetch_github_repo(url: str, branch: str, docs_path: str) -> tuple[bool, str]`
  - Clone or fetch repo content via GitHub API
  - Save to docs/github/{owner}_{repo}/
  - Handle private repos (error message for now)
  - Return (success, message)

- `cleanup_on_error(docs_path: str)`
  - Remove partially created docs folder on failure

#### 2.4.3 `session_state.py`

**Functions**:
- `init_session_state()`
  - Initialize all session state variables with defaults

- `reset_session()`
  - Clear all session state and reinitialize

- `get_current_step() -> int`
  - Return current step from session state

- `set_current_step(step: int)`
  - Update current step in session state

- `add_vtt_file(file)`
- `remove_vtt_file(index: int)`
- `get_vtt_files() -> list`
- Similar functions for code_files and github_urls

---

## 3. Page Specifications

### 3.1 `landing.py` (Step 0)

**Layout:**
- Full-width hero section with gradient background
- App title: "Class Recording RAG"
- Subtitle: "Upload your class recordings, code files, and GitHub repos to build a searchable knowledge base"
- Centered "Get Started" button (large, primary)

**Features Section (below fold):**
Three cards in a row:
1. **Upload VTT Files** - "Upload subtitle files from your class recordings"
2. **Add Code Files** - "Include code files discussed in the class"
3. **Connect GitHub** - "Link GitHub repositories for reference"

**Footer:**
- "Built with Streamlit"

### 3.2 `vtt_upload.py` (Step 1)

**Layout:**
- Step indicator at top
- Page title: "Upload VTT Subtitle Files"
- Subtitle: "Upload the subtitle files from your class recordings (.vtt format)"

**Upload Section:**
- Large drag-and-drop zone with file icon
- Accept: `.vtt` files
- Multiple files allowed
- Help text: "You can upload multiple VTT files from different class sessions"

**File List Section (appears after upload):**
- Table with columns: File Name, Size, Actions
- Remove button per file
- Total count badge

**Preview Section:**
- Collapsible: "Preview first file"
- Show first 500 characters with scrollable text area

**Navigation:**
- "Continue to Code Files" button (disabled if no files)
- "Back" button (returns to landing, clears progress)

### 3.3 `code_upload.py` (Step 2)

**Layout:**
- Step indicator
- Page title: "Upload Code Files (Optional)"
- Subtitle: "Do you have any code files that were discussed in the class?"

**Selection:**
- Two large button options side by side:
  - **Yes, I have code files** (with document icon)
  - **No, skip this step** (with skip/arrow icon)

**If "Yes" selected:**
- File uploader appears:
  - Accept: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.cpp`, `.c`, `.go`, `.rs`, `.rb`, `.php`, `.sql`, `.html`, `.css`, `.json`, `.yaml`, `.yml`, `.md`
  - Multiple files allowed
  - Max file size: 10MB per file
- File list with:
  - File icon based on extension
  - File name
  - Language detection badge
  - Size
  - Remove button
- Language summary: "Python (3), JavaScript (2), Other (1)"

**Navigation:**
- "Continue to GitHub" button
- "Back" button (to VTT step)

### 3.4 `github_upload.py` (Step 3)

**Layout:**
- Step indicator
- Page title: "Add GitHub Repositories (Optional)"
- Subtitle: "Do you have any GitHub repositories you'd like to include?"

**Selection:**
- Two button options:
  - **Yes, I have GitHub repos** (GitHub icon)
  - **No, skip this step** (skip icon)

**If "Yes" selected:**
- URL input section:
  - Label: "Repository URL"
  - Text input with placeholder: "https://github.com/owner/repo"
  - Validation in real-time:
    - Green checkmark if valid
    - Red X with error message if invalid
  - Help text: "Enter the full GitHub repository URL"
- "Add Another Repository" button (adds new URL field)
- Dynamic URL list:
  - Each URL field has remove button (disabled if only one)
  - Branch selector dropdown (defaults to "main", options: main, master, other)
  - If "other" selected: text input for branch name
- Summary section:
  - "X repositories ready to fetch"
  - List of valid repos with owner/repo name extracted

**URL Validation Rules:**
- Must start with `https://github.com/`
- Must match pattern: `github.com/{owner}/{repo}`
- Remove trailing slashes and `.git` suffix automatically
- Owner and repo names: alphanumeric, hyphens, underscores

**Navigation:**
- "Review and Submit" button (enabled when all URLs valid or empty)
- "Back" button (to code upload step)

### 3.5 `review.py` (Step 4)

**Layout:**
- Step indicator
- Page title: "Review Your Uploads"
- Subtitle: "Please review your files before processing"

**Summary Cards (3 cards in a row if space permits, else stacked):**

**Card 1: VTT Files**
- Header: Green background, document icon
- Content:
  - Large number: "X files"
  - List of filenames (scrollable if >5)
  - Total size
- Footer: "Edit" link (navigates to Step 1)

**Card 2: Code Files**
- Header: Blue background, code icon
- Content:
  - Large number: "X files" or "None"
  - Language breakdown (badges)
  - List of filenames (if files present)
- Footer: "Edit" link (navigates to Step 2)

**Card 3: GitHub Repositories**
- Header: Purple background, GitHub icon
- Content:
  - Large number: "X repos" or "None"
  - List of owner/repo names
  - Branch info
- Footer: "Edit" link (navigates to Step 3)

**Storage Information:**
- Info box: "All files will be saved to: `{docs_path}`"
- Storage estimate

**Action Section:**
- Large "Process and Save" button (primary, full-width)
- "Or go back to edit" link

**Terms/Disclaimer (small text):**
- "By processing, files will be saved locally and prepared for RAG indexing"

### 3.6 `success.py` (Step 5)

**Layout:**
- Step indicator (all steps complete)
- Large success animation/illustration at top
- Page title: "Upload Complete!"
- Subtitle: "Your files have been successfully processed"

**Summary Section:**
- Card showing:
  - Total files saved
  - Breakdown by type with icons:
    - VTT: X files
    - Code: X files (Y languages)
    - GitHub: X repositories
  - Total storage used
  - Location: `{docs_path}`

**File Explorer Preview (optional):**
- Collapsible tree view of saved files
- Folder structure visualization

**Action Buttons (2-3 in a row):**
- **"Start New Upload"** (primary) - Resets form to Step 0
- **"Go to Chat"** (secondary, disabled) - Placeholder for future RAG chat
- **"Open docs/ Folder"** (secondary) - Opens file explorer to docs path

**Help Section:**
- "What's next?" card with:
  - "Your files are now ready for RAG processing"
  - "You can start a new upload or wait for the chat interface"
  - Link to documentation (future)

**Footer:**
- Session info, timestamp

---

## 4. Supporting Modules

### 4.1 `styles/custom_css.py`

**Function**: `get_custom_css() -> str`

Returns CSS string for:
- Global resets and typography
- Header/hero section styles
- Card component styles
- Button variants (primary, secondary, danger)
- Step indicator styles
- Form input styles
- Animation keyframes (pulse, fade-in, slide-in)

### 4.2 `utils/validators.py`

**Functions**:
- `validate_vtt_file(file) -> ValidationResult`
- `validate_code_file(file) -> ValidationResult`
- `validate_github_url(url: str) -> ValidationResult`
- `normalize_github_url(url: str) -> str`
- `extract_repo_info(url: str) -> dict`

**ValidationResult TypedDict**:
```python
{
    "is_valid": bool,
    "error_message": str | None,
    "parsed_data": dict | None
}
```

### 4.3 `utils/file_handler.py`

**Functions**:
- `ensure_docs_folder(base_path: str) -> str`
- `save_vtt_files(files: list, docs_path: str) -> list[str]`
- `save_code_files(files: list, docs_path: str) -> list[str]`
- `fetch_github_repo(url: str, branch: str, docs_path: str) -> FetchResult`
- `cleanup_docs_folder(docs_path: str)`
- `get_storage_stats(docs_path: str) -> dict`

**FetchResult TypedDict**:
```python
{
    "success": bool,
    "message": str,
    "saved_path": str | None,
    "files_count": int
}
```

### 4.4 `utils/session_state.py`

**Functions**:
- `init_session_state()`
- `reset_session_state()`
- `get_state(key: str) -> any`
- `set_state(key: str, value: any)`
- `add_to_list(key: str, value: any)`
- `remove_from_list(key: str, index: int)`

---

## 5. Streamlit Configuration

### 5.1 `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#4F46E5"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8FAFC"
textColor = "#1E293B"
font = "sans-serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = true

[runner]
fastReruns = true
```

### 5.2 `requirements.txt`

```
streamlit>=1.28.0
requests>=2.31.0
validators>=0.22.0
pathlib>=1.0.1
```

---

## 6. Navigation Flow

```
┌─────────────┐
│   Landing   │
│   (Step 0)  │
└──────┬──────┘
       │ Get Started
       ▼
┌─────────────┐
│   VTT       │
│   (Step 1)  │◄─────────┐
└──────┬──────┘          │
       │ Continue        │ Edit (from Review)
       ▼                 │
┌─────────────┐          │
│   Code      │          │
│   (Step 2)  │◄─────────┤
└──────┬──────┘          │
       │ Continue        │ Edit
       ▼                 │
┌─────────────┐          │
│   GitHub    │          │
│   (Step 3)  │◄─────────┤
└──────┬──────┘          │
       │ Review          │ Edit
       ▼                 │
┌─────────────┐          │
│   Review    │─────────┘
│   (Step 4)  │
└──────┬──────┘
       │ Process
       ▼
┌─────────────┐
│   Success   │
│   (Step 5)  │
└─────────────┘
```

---

## 7. Error Handling Strategy

### 7.1 Error Types and Handling

| Error Type | Display | Action |
|------------|---------|--------|
| Invalid file type | Inline error below uploader | Block continue, allow retry |
| File too large | Toast notification + inline error | Block continue, suggest compression |
| Invalid GitHub URL | Inline error on input | Disable continue until fixed |
| Network error (GitHub) | Toast + inline error | Retry button, manual skip option |
| Disk space full | Modal dialog | Cleanup suggestion, cancel option |
| Permission denied | Toast + inline error | Suggest alternate location |

### 7.2 Error Display Components

- **Toast notifications**: `st.toast()` for transient errors
- **Inline errors**: Red text below relevant input
- **Modal dialogs**: `st.dialog()` for blocking errors requiring user decision
- **Banner**: Full-width error at top for critical issues

---

## 8. Testing Checklist

### 8.1 Functional Tests

- [ ] Landing page renders correctly
- [ ] Step indicator updates with each step
- [ ] VTT upload accepts .vtt files only
- [ ] Multiple VTT files can be uploaded
- [ ] File removal works correctly
- [ ] Cannot proceed without VTT files
- [ ] Code file step can be skipped
- [ ] Code files validate by extension
- [ ] GitHub step can be skipped
- [ ] GitHub URLs validate correctly
- [ ] Invalid URLs block continue
- [ ] Review page shows all uploads
- [ ] Edit links navigate to correct steps
- [ ] Process button saves all files
- [ ] Success page shows summary
- [ ] New upload resets form

### 8.2 UI/UX Tests

- [ ] App is responsive on different screen sizes
- [ ] Custom CSS renders correctly
- [ ] Step indicator shows correct state
- [ ] Buttons have proper hover states
- [ ] Loading states are visible
- [ ] Error messages are clear and helpful
- [ ] Success animations play correctly

### 8.3 Edge Cases

- [ ] Zero-byte files
- [ ] Very large files (>100MB)
- [ ] Special characters in filenames
- [ ] Unicode filenames
- [ ] Network interruption during GitHub fetch
- [ ] Disk full during save
- [ ] Permission errors
- [ ] Concurrent sessions

---

## 9. Implementation Phases

### Phase 1: Core Structure
1. Create folder structure
2. Set up `app.py` with basic routing
3. Implement `session_state.py`
4. Create `config.toml`

### Phase 2: UI Components
1. Implement `custom_css.py`
2. Create `step_indicator.py`
3. Create `file_uploader.py`
4. Create `github_input.py`
5. Create `review_card.py`

### Phase 3: Pages
1. Implement `landing.py`
2. Implement `vtt_upload.py`
3. Implement `code_upload.py`
4. Implement `github_upload.py`
5. Implement `review.py`
6. Implement `success.py`

### Phase 4: Utils & Validation
1. Implement `validators.py`
2. Implement `file_handler.py`
3. Wire up file operations to UI

### Phase 5: Polish
1. Test all flows
2. Fix edge cases
3. Refine CSS and animations
4. Add error handling
5. Performance optimization

---

## 10. Appendix

### 10.1 Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #4F46E5 | Buttons, active states, links |
| Primary Dark | #4338CA | Hover states |
| Secondary | #64748B | Secondary buttons, muted text |
| Success | #10B981 | Success states, checkmarks |
| Warning | #F59E0B | Warnings, caution |
| Error | #EF4444 | Errors, invalid states |
| Background | #F8FAFC | Page background |
| Card | #FFFFFF | Card backgrounds |
| Text | #1E293B | Primary text |
| Text Muted | #64748B | Secondary text |

### 10.2 Typography

| Element | Font | Size | Weight |
|---------|------|------|--------|
| H1 (Page Title) | System UI | 32px | 700 |
| H2 (Section) | System UI | 24px | 600 |
| H3 (Card Title) | System UI | 18px | 600 |
| Body | System UI | 16px | 400 |
| Small | System UI | 14px | 400 |
| Caption | System UI | 12px | 400 |

### 10.3 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Tight spacing, icon padding |
| sm | 8px | Button padding, small gaps |
| md | 16px | Standard spacing, card padding |
| lg | 24px | Section spacing, large gaps |
| xl | 32px | Major section breaks |
| 2xl | 48px | Page-level spacing |

### 10.4 Icons (Unicode/Emoji)

| Usage | Icon | Unicode |
|-------|------|---------|
| Upload | 📁 | U+1F4C1 |
| File | 📄 | U+1F4C4 |
| Code | 💻 | U+1F4BB |
| GitHub | 🐙 | U+1F419 |
| Check | ✓ | U+2713 |
| Success | ✓ | U+2713 |
| Error | ✗ | U+2717 |
| Warning | ⚠ | U+26A0 |
| Info | ℹ | U+2139 |
| Arrow Right | → | U+2192 |
| Arrow Left | ← | U+2190 |
| Refresh | ↻ | U+21BB |
| Folder | 📂 | U+1F4C2 |
| Star | ★ | U+2605 |

---

## End of Specification
