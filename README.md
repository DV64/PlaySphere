# 🎮 PlaySphere | بلاي سفير

<div align="center">
  <br>
  <p><strong>Advanced Game Search Engine | محرك بحث متقدم للألعاب</strong></p>
</div>

<div align="center">
  <a href="#english">English</a> | 
  <a href="#arabic">العربية</a>
</div>

---

<a name="english"></a>
## 🇬🇧 English

### 📋 Overview

PlaySphere is an advanced game search engine that allows users to search across multiple game sources simultaneously. It aggregates results from more than 8 different game repositories, providing a unified search experience with a modern, responsive interface.

### ✨ Features

- **Multi-source Search**: Search across 8+ game repositories at once
- **Source Filtering**: Choose which sources to include in your search
- **Bilingual Support**: Full Arabic and English language support
- **Responsive Design**: Works perfectly on all devices
- **Advanced Sorting**: Sort results by title, source, or date
- **Modern UI**: Beautiful, user-friendly interface with dark mode

### 🛠️ Project Components

The project consists of two main parts:

1. **Frontend**: HTML/CSS/JavaScript files that provide the user interface
   - `index.html`: Main application with responsive UI
   - `assets/`: Directory containing images, CSS, and JavaScript files

2. **Backend**: Python Flask server that handles the search requests
   - `server.py`: The main server application with search functionality
   - `translations_ar.py`: Arabic language translations
   - `translations_en.py`: English language translations

### 🔧 How to Run PlaySphere

#### Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

#### Setup and Run

1. **Clone or download the project files**

2. **Create and activate a virtual environment**:
   ```bash
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**:
   ```bash
   python server.py
   ```

5. **Access the application**:
   Open your browser and navigate to http://localhost:5000

### 💻 How to Use

1. **Select Game Sources**: Use the checkboxes to select which game repositories you want to search
2. **Enter Search Query**: Type your game title in the search box
3. **Start Search**: Click the search button or press Enter
4. **Browse Results**: View the unified search results from all selected sources
5. **Sort Results**: Use the sort options to organize results by title, source, or date
6. **Switch Language**: Toggle between Arabic and English using the language button

### 📂 Project Structure

```
PlaySphere/
├── assets/                 # Static assets (images, icons, CSS, JS)
├── .vscode/                # VS Code configuration
├── .gitignore              # Git ignore rules
├── index.html              # Main frontend HTML file
├── README.md               # Documentation file
├── requirements.txt        # Python dependencies
├── server.py               # Main server application
├── translations_ar.py      # Arabic translations
└── translations_en.py      # English translations
```

### 🔄 Server API

The server provides two main API endpoints:

- **GET /search**: Searches across game sources
  - Parameters: `q` (query), `sources` (comma-separated list of sources)
  - Example: `/search?q=minecraft&sources=fitgirl,ocean`

- **GET /translations**: Fetches UI translations
  - Parameters: `lang` (ar or en)
  - Example: `/translations?lang=ar`

### 📝 License

This project is licensed under the GNU General Public License (GPL) - a free, copyleft license for software that guarantees end users the freedom to run, study, share, and modify the software. For more information, visit [GNU GPL website](https://www.gnu.org/licenses/gpl-3.0.html).

### ⚠️ Disclaimer

This project is for educational purposes only. The developers are not responsible for any misuse of this application. PlaySphere simply aggregates search results from various sources and does not host any game files. Users are responsible for ensuring they comply with all applicable laws and regulations in their jurisdiction regarding game downloads and usage.

---

<a name="arabic"></a>
## 🇸🇦 العربية

### 📋 نظرة عامة

بلاي سفير هو محرك بحث متقدم للألعاب يتيح للمستخدمين البحث عبر مصادر متعددة للألعاب في وقت واحد. يجمع النتائج من أكثر من 8 مواقع مختلفة للألعاب، مما يوفر تجربة بحث موحدة مع واجهة حديثة ومتجاوبة.

### ✨ المميزات

- **بحث متعدد المصادر**: ابحث في أكثر من 8 مواقع للألعاب في وقت واحد
- **تصفية المصادر**: اختر المصادر التي تريد تضمينها في بحثك
- **دعم ثنائي اللغة**: دعم كامل للغتي العربية والإنجليزية
- **تصميم متجاوب**: يعمل بشكل مثالي على جميع الأجهزة
- **فرز متقدم**: رتب النتائج حسب العنوان أو المصدر أو التاريخ
- **واجهة مستخدم حديثة**: واجهة جميلة وسهلة الاستخدام مع الوضع الداكن

### 🛠️ مكونات المشروع

يتكون المشروع من جزئين رئيسيين:

1. **الواجهة الأمامية**: ملفات HTML/CSS/JavaScript التي توفر واجهة المستخدم
   - `index.html`: التطبيق الرئيسي مع واجهة مستخدم متجاوبة
   - `assets/`: مجلد يحتوي على الصور وملفات CSS و JavaScript

2. **الخادم الخلفي**: خادم Python Flask الذي يعالج طلبات البحث
   - `server.py`: تطبيق الخادم الرئيسي مع وظائف البحث
   - `translations_ar.py`: ترجمات اللغة العربية
   - `translations_en.py`: ترجمات اللغة الإنجليزية

### 🔧 كيفية تشغيل بلاي سفير

#### المتطلبات المسبقة

- Python 3.7 أو أحدث
- متصفح ويب حديث (Chrome، Firefox، Edge، Safari)

#### الإعداد والتشغيل

1. **استنساخ أو تحميل ملفات المشروع**

2. **إنشاء وتفعيل بيئة افتراضية**:
   ```bash
   # لنظام Windows
   python -m venv venv
   venv\Scripts\activate

   # لنظام macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **تثبيت الحزم المطلوبة**:
   ```bash
   pip install -r requirements.txt
   ```

4. **تشغيل الخادم**:
   ```bash
   python server.py
   ```

5. **الوصول إلى التطبيق**:
   افتح متصفحك وانتقل إلى http://localhost:5000

### 💻 كيفية الاستخدام

1. **اختيار مصادر الألعاب**: استخدم مربعات الاختيار لتحديد مستودعات الألعاب التي تريد البحث فيها
2. **إدخال استعلام البحث**: اكتب عنوان اللعبة في مربع البحث
3. **بدء البحث**: انقر على زر البحث أو اضغط على Enter
4. **تصفح النتائج**: اعرض نتائج البحث الموحدة من جميع المصادر المحددة
5. **فرز النتائج**: استخدم خيارات الفرز لتنظيم النتائج حسب العنوان أو المصدر أو التاريخ
6. **تبديل اللغة**: التبديل بين العربية والإنجليزية باستخدام زر اللغة

### 📂 هيكل المشروع

```
PlaySphere/
├── assets/                 # الأصول الثابتة (الصور والأيقونات، CSS، JS)
├── .vscode/                # إعدادات VS Code
├── .gitignore              # قواعد تجاهل Git
├── index.html              # ملف HTML الرئيسي للواجهة الأمامية
├── README.md               # ملف التوثيق
├── requirements.txt        # تبعيات Python
├── server.py               # تطبيق الخادم الرئيسي
├── translations_ar.py      # الترجمات العربية
└── translations_en.py      # الترجمات الإنجليزية
```

### 🔄 واجهة برمجة الخادم

يوفر الخادم نقطتي وصول رئيسيتين لواجهة برمجة التطبيقات:

- **GET /search**: يبحث عبر مصادر الألعاب
  - المعلمات: `q` (الاستعلام)، `sources` (قائمة مصادر مفصولة بفواصل)
  - مثال: `/search?q=minecraft&sources=fitgirl,ocean`

- **GET /translations**: يجلب ترجمات واجهة المستخدم
  - المعلمات: `lang` (ar أو en)
  - مثال: `/translations?lang=ar`

### 📝 الترخيص

هذا المشروع مرخص تحت رخصة (GNU General Public License - GPL) - وهي رخصة حرة للبرمجيات تضمن للمستخدمين النهائيين حرية تشغيل البرنامج ودراسته ومشاركته وتعديله. لمزيد من المعلومات، يمكنك زيارة [موقع رخصة GNU GPL](https://www.gnu.org/licenses/gpl-3.0.html).

### ⚠️ تنبيه

هذا المشروع لأغراض تعليمية فقط. المطورون غير مسؤولين عن أي سوء استخدام لهذا التطبيق. يقوم بلاي سفير فقط بتجميع نتائج البحث من مصادر مختلفة ولا يستضيف أي ملفات ألعاب. المستخدمون مسؤولون عن ضمان امتثالهم لجميع القوانين واللوائح المعمول بها في نطاقهم القضائي فيما يتعلق بتنزيل الألعاب واستخدامها.
