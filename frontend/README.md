# John A. Macdonald History Bot - Frontend

A Vue 3 frontend application that provides a conversational interface to interact with Sir John A. Macdonald, Canada's first Prime Minister, using historical documents and AI-powered responses.

## 🎨 Features

- **Victorian-inspired Design**: Clean, elegant interface with period-appropriate styling
- **Interactive Q&A**: Ask questions and receive historically-grounded responses
- **Source References**: Collapsible section showing historical excerpts that informed each response
- **Follow-up Suggestions**: Smart suggestions for continuing the conversation
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Smooth Animations**: Fade-in transitions and interactive hover effects

## 🏗️ Architecture

Built with **Vue 3 Composition API** and organized into modular components:

- **App.vue**: Main layout and state management
- **QuestionInput.vue**: User question input with Victorian styling
- **MacdonaldResponse.vue**: Displays responses in a journal-style format
- **SourceQuotes.vue**: Collapsible historical source excerpts
- **FollowUpSuggestions.vue**: Clickable follow-up question suggestions

## 🚀 Getting Started

### Prerequisites

- Node.js (version 16 or higher)
- npm or yarn
- The backend API running on `http://localhost:8000`

### Installation

1. **Clone the repository and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser and visit:**
   ```
   http://localhost:3000
   ```

### Build for Production

```bash
npm run build
```

The built files will be available in the `dist` directory.

## 🎯 API Integration

The frontend expects your FastAPI backend to be running on `http://localhost:8000` with the following endpoint:

### POST `/ask`

**Request Body:**
```json
{
  "question": "Why did you support Confederation?"
}
```

**Expected Response:**
```json
{
  "question": "Why did you support Confederation?",
  "answer": "I supported Confederation because...",
  "sources": [
    {
      "quote": "We must have a strong central government...",
      "source": "Hansard_1865.pdf",
      "page": 34,
      "year": 1865
    }
  ],
  "follow_ups": [
    "What role did George Brown play?",
    "Why were the Maritimes hesitant to join?"
  ]
}
```

## 🎨 Design System

### Typography
- **Headers & Response Text**: EB Garamond (serif)
- **Body Text**: Crimson Text (serif)
- **Victorian aesthetic** with large, readable font sizes

### Color Palette
- **Primary**: `#2c2c2c` (Dark charcoal)
- **Background**: `#fafafa` (Off-white)
- **Text**: `#1a1a1a` (Near black)
- **Accents**: `#666` (Medium gray)

### Components
- **Journal-style response box** with ornamental elements
- **Clean, bordered input** with Victorian styling
- **Collapsible references** with smooth animations
- **Interactive suggestion buttons** with hover effects

## 📱 Responsive Design

The application is fully responsive with breakpoints at:
- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: < 768px

## 🔧 Configuration

### Vite Configuration

The app includes a proxy configuration to forward API requests to your backend:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/ask': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### Environment Variables

You can create a `.env` file in the frontend directory to customize settings:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 🛠️ Development

### Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── QuestionInput.vue
│   │   ├── MacdonaldResponse.vue
│   │   ├── SourceQuotes.vue
│   │   └── FollowUpSuggestions.vue
│   ├── App.vue
│   └── main.js
├── index.html
├── package.json
└── vite.config.js
```

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## 🔍 Features in Detail

### Question Input
- Large, accessible textarea
- Disabled state during loading
- Enter key support (Shift+Enter for new line)
- Auto-fill from follow-up suggestions

### Response Display
- Victorian journal aesthetic with ornamental elements
- Fade-in animation when responses load
- Date stamp and signature
- Elegant typography optimized for readability

### Source References
- Collapsible panel with smooth expand/collapse
- Formatted historical excerpts with proper citations
- Source document name cleaning and formatting
- Page numbers and year information

### Follow-up Suggestions
- Animated suggestion buttons with hover effects
- Click to auto-fill and submit new questions
- Staggered entrance animations
- Responsive button layout

## 🎭 Error Handling

The application gracefully handles:
- API connection failures
- Loading states with animated indicators
- Empty or malformed responses
- Network timeouts

## 📝 Browser Support

Modern browsers supporting:
- ES6+ features
- CSS Grid and Flexbox
- CSS Custom Properties
- Modern JavaScript APIs

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🤝 Contributing

When contributing to the frontend:

1. Follow the existing component structure
2. Maintain the Victorian design aesthetic
3. Ensure responsive design on all screen sizes
4. Test accessibility features
5. Add appropriate animations and transitions

---

*Experience history through conversation with Canada's founding father.*