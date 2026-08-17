# Universal XeLaTeX College Report Construction Guide

> **Master Baseline Blueprint**: A domain-agnostic, step-by-step master guide for humans and AI agents (such as Antigravity / Gemini) to build publication-grade, professionally accepted academic project reports on **ANY subject or domain** for **ANY college or university worldwide** from absolute scratch, built strictly upon the baseline specifications of `biraj-xelatex-general-specs.md`.

---

## Zero-to-PDF: Building a Polished Report From Scratch

Following this guide allows any student, researcher, or AI coding agent to start from an empty folder and build a complete, publication-grade academic report that is immediately accepted by university examination boards.

### Required Directory Structure
Create the following folder layout in your workspace root:

```
Your-Project-Name/
│
├── images/                                       # Root directory for all images & diagrams
│   ├── institution-logo.png                      # College / University logo
│   ├── block-diagram.png                         # System architecture diagram
│   ├── schematic.png                             # Circuit or technical schematic
│   └── photo1.jpg - photoN.jpg                   # Hardware / Experimental setup photos
│
├── Your-Project-Name-Report.tex                  # Main XeLaTeX source file
├── compile_xelatex.ps1                           # PowerShell double-pass compile script
└── README.md                                     # Main repository documentation
```

---

## Core Execution Directive for AI Agents & Human Authors

> **BEFORE WRITING A SINGLE LINE OF LATEX CODE:**
> 1. **Analyze Requirements Carefully**: Thoroughly analyze the user's prompt, project domain, hardware/software specifications, chapter requirements, data files, and specific university guidelines.
> 2. **Apply Sense & Domain Engineering**: Structure chapters logically for the project type (e.g. Hardware/Robotics vs Pure AI/Software vs Mechanical/Civil).
> 3. **Obey Baseline Specifications Strictly**: Enforce exact typographic scaling, hyphenation penalties, non-justified text wrapping, list-only paragraph indentation, full-grid table rules, breakable code blocks, and page budget limits.
> 4. **Mandatory Final Chapters & Citations**: Every report **MUST** conclude with a **Conclusion and Future Scope** chapter followed by a **References** chapter containing **at least 10 domain-tailored technical/academic references** cited throughout the text using `\cite{...}`.

---

## Baseline Specifications & Technical Standards Summary

| Category | Specification Standard | Exact LaTeX Command / Setting |
| :--- | :--- | :--- |
| **Document Class** | A4 Paper, Single-Sided Report | `\documentclass[12pt,a4paper,oneside]{report}` |
| **Page Margins** | Uniform 0.8 in (2.0 cm) all sides | `\usepackage[margin=0.8in]{geometry}` |
| **Main Font** | Times New Roman (or TeX Gyre Pagella) | `\setmainfont{Times New Roman}` |
| **Monospace Font** | Courier New @ 88% Scale | `\setmonofont[Scale=0.88]{Courier New}` |
| **Global Line Spacing** | 1.2 Line Height Baseline | `\setstretch{1.2}` |
| **Paragraph Setup** | 0pt Indent, 5pt Paragraph Skip | `\setlength{\parindent}{0pt}`, `\setlength{\parskip}{5pt}` |
| **Text Alignment** | Left-Aligned (NO Content Justification)| `\raggedright` |
| **Indentation Rule** | List / Bullet Points Only | `\begin{enumerate}[noitemsep,topsep=2pt,parsep=0pt]` |
| **Hyphenation Control**| Hyphenation Disabled Globally | `\hyphenpenalty=10000`, `\exhyphenpenalty=10000` |
| **Margin Overflow Fix**| Emergency Stretch & Sloppy Wrapping | `\emergencystretch=3em`, `\sloppy` |
| **Chapter Placement** | Fresh New Page Onwards | `\clearpage` before every `\chapter{...}` |
| **Header & Footer** | No Branding, Centered Page Number | `\fancyhf{}`, `\cfoot{\thepage}`, `\headrulewidth 0pt` |
| **TOC Budget Control**| Chapter-wise & Topic-wise TOC (1 Page)| `\setcounter{tocdepth}{1}` |
| **Hyperlink Styling** | All Black Except Purple Citations | `\usepackage[colorlinks=true,linkcolor=black,citecolor=black,urlcolor=black]{hyperref}` |
| **Final Chapters** | Conclusion & 10+ References Mandatory | `\chapter{Conclusion...}`, `\begin{thebibliography}{99}` |

---

## Root `images/` Directory Management & Dynamic Captioning

All report images (logos, block diagrams, circuit schematics, graphs, prototype photos) **MUST** be placed inside an `images/` folder located at the root of the project directory.

### 1. Preamble Graphics Path Setup
In your preamble, declare `graphicx`, `caption`, and `subcaption`, and set the search path to the root `images/` folder:

```latex
\usepackage{graphicx}
\usepackage{caption}
\usepackage{subcaption}

% Set graphicspath to search the root images/ folder automatically
\graphicspath{{images/}}
```

---

### 2. Dynamic Caption Numbering & Naming Rules

LaTeX automatically calculates chapter-based dynamic figure, table, and listing numbers (`Figure 1.1`, `Figure 2.1`, `Table 1.1`, `Listing 4.1`) based on the chapter counter (`\thechapter`).

#### Strict Placement Rules:
1. **Figure Captions**: Place `\caption{...}` **BELOW** the image graphics.
2. **Table Captions**: Place `\captionof{table}{...}` **BELOW** (or above) the tabular environment consistently.
3. **Listing Captions**: Place listing titles **ABOVE** the listing box or as part of the `tcolorbox` title bar.
4. **Label Sequence Rule**: The `\label{...}` command **MUST ALWAYS BE PLACED IMMEDIATELY AFTER** `\caption{...}` or `\captionof{...}`. Placing `\label{...}` before `\caption{...}` breaks cross-referencing and leads to incorrect figure numbers in text.

---

### 3. Native Image Insertion Examples

#### A. Standard Floating Figure Environment
Use the floating `figure` environment for automatic, dynamic chapter-relative figure numbering (`Figure 1.1`, `Figure 2.1`):

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.55\textwidth,height=5.5cm,keepaspectratio=true]{comp-img1.jpeg}
  \caption{Transmitter Hardware Glove Assembly with ESP32 and MPU6050 IMU}
  \label{fig:tx_glove_spec}
\end{figure}
```
*Note*: Cross-referencing in text via `\ref{fig:tx_glove_spec}` dynamically outputs **Figure \ref{fig:tx_glove_spec}**.

#### B. Non-Floating Center Figures (Prevents Floating Drift across Pages)
In tight university layouts where floating figures might drift across page boundaries, use non-floating `center` environments combined with `\captionof{figure}{...}`:

```latex
\begin{center}
\includegraphics[width=0.55\textwidth,height=5.5cm,keepaspectratio=true]{comp-img2.jpeg}
\captionof{figure}{Receiver Chassis Hardware with Dual L298N Drivers and ESP32}
\label{fig:rx_chassis_spec}
\end{center}
```

#### C. Handling Oversized Diagrams & Schematics
When an architecture diagram or circuit schematic exceeds standard text width, wrap it in a centered `makebox` to prevent margin overflow:

```latex
\begin{center}
\makebox[\textwidth][c]{\includegraphics[width=0.85\textwidth,height=6.5cm,keepaspectratio=true]{block-diagram.png}}
\captionof{figure}{Complete System Architecture Diagram}
\label{fig:block_diagram_spec}
\end{center}
```

#### D. Side-by-Side Subfigure Grids
For placing multiple related images side-by-side with sub-captions `(a)` and `(b)`:

```latex
\begin{figure}[htbp]
  \centering
  \begin{subfigure}[b]{0.45\textwidth}
    \centering
    \includegraphics[width=\textwidth,height=4.5cm,keepaspectratio=true]{final_transmitter.png}
    \caption{Hand Transmitter Glove}
    \label{fig:sub_tx}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.45\textwidth}
    \centering
    \includegraphics[width=\textwidth,height=4.5cm,keepaspectratio=true]{final_receiver_on_car.png}
    \caption{Assembled 4WD Vehicle}
    \label{fig:sub_rx}
  \end{subfigure}
  \caption{Physical Hardware Prototype Realization}
  \label{fig:hardware_grid}
\end{figure}
```

---

## Conclusion Chapter & 10+ References Citation Guide

Every report **MUST** conclude with two mandatory final chapters: a **Conclusion and Future Scope** chapter and a **References** chapter containing **at least 10 domain-specific technical references**.

### 1. Mandatory Conclusion & Future Scope Chapter Structure
The conclusion chapter summarizes technical achievements, quantitative results, and practical utility, followed by structured future enhancements:

```latex
\clearpage
\chapter{CONCLUSION AND FUTURE SCOPE}

\section{Conclusion}
This project successfully designed, implemented, and validated an embedded hand-gesture-controlled robotic vehicle using ESP32 microcontrollers, an MPU6050 IMU sensor, and ESP-NOW wireless communication. The prototype achieved zero-packet-loss transmission over a 15-meter line-of-sight range with an average end-to-end control latency of 18.4 ms. The dual L298N motor driver configuration demonstrated robust traction control across differential steering modes.

\section{Future Work and Enhancements}
To build upon the foundation established in this project, future enhancements will focus on:
\begin{enumerate}[noitemsep,topsep=2pt,parsep=0pt]
  \item \textbf{Computer Vision Integration}: Incorporating an onboard ESP32-CAM or Raspberry Pi module for real-time video streaming and vision-based object detection.
  \item \textbf{Obstacle Avoidance Autonomy}: Integrating Ultrasonic HC-SR04 sensors with automated emergency braking logic to prevent collisions during manual gesture control.
  \item \textbf{Flex Sensor Hybrid Control}: Combining accelerometer tilt sensing with flex sensors to enable fine-grained finger articulation control.
  \item \textbf{LiPo Battery Management System (BMS)}: Implementing active cell balancing and battery telemetry monitoring for improved power efficiency.
\end{enumerate}
```

---

### 2. In-Text Citation Placement Rule
Throughout the report body (Literature Review, System Design, Component Specs, Communication Protocols), authors **MUST** place in-text citations using `\cite{ref_key}`:

- **Literature Review**: Cite foundational research papers, e.g., *"Gesture recognition techniques have evolved significantly from glove-based sensors to vision systems \cite{ref_gesture_survey, ref_imu_accel}."*
- **Microcontroller & Hardware Specs**: Cite manufacturer datasheets, e.g., *"The ESP32 microcontroller features a dual-core Xtensa LX6 processor operating at 240 MHz \cite{ref_esp32_datasheet}."*
- **Wireless Protocols**: Cite IEEE standards and RFCs, e.g., *"ESP-NOW leverages peer-to-peer vendor-specific action frames compliant with IEEE 802.11 standards \cite{ref_espnow_doc, ref_ieee_80211}."*
- **Motor Control & Kinematics**: Cite textbooks, e.g., *"Differential drive vehicle kinematics govern vehicle turning radius and rotational velocity \cite{ref_robotics_textbook}."*

---

### 3. Mandatory 10+ References Bibliography Template

The `thebibliography` environment **MUST contain at least 10 detailed, domain-relevant entries**:

```latex
\clearpage
\begin{thebibliography}{99}
\bibitem{ref_esp32_datasheet}
Espressif Systems, \textit{ESP32 Series Datasheet: Dual-Core Wi-Fi \& Bluetooth MCU}, v4.1, Espressif Systems, 2024.

\bibitem{ref_mpu6050_manual}
InvenSense Inc., \textit{MPU-6050 Product Specification and Register Map}, Rev. 3.4, InvenSense, 2021.

\bibitem{ref_espnow_doc}
Espressif Systems, \textit{ESP-NOW Technical Reference Manual: Peer-to-Peer Wireless Communication}, Espressif Documentation, 2023.

\bibitem{ref_l298n_datasheet}
STMicroelectronics, \textit{L298 Dual Full-Bridge Driver Datasheet}, STMicroelectronics Doc ID 1333, 2020.

\bibitem{ref_gesture_survey}
A. Smith and B. Johnson, ``Survey of Motion-Based Gesture Recognition Interfaces for Mobile Robotics,'' \textit{IEEE Transactions on Human-Machine Systems}, vol. 51, no. 3, pp. 245--258, 2021.

\bibitem{ref_imu_accel}
C. Miller, D. Lee, and E. Patel, ``MEMS Inertial Sensor Fusion for Real-Time Gesture Tracking,'' \textit{Sensors and Actuators A: Physical}, vol. 312, p. 112104, 2022.

\bibitem{ref_robotics_textbook}
R. Siegwart, I. R. Nourbakhsh, and D. Scaramuzza, \textit{Introduction to Autonomous Mobile Robots}, 2nd ed., MIT Press, Cambridge, MA, 2011.

\bibitem{ref_ieee_80211}
IEEE Computer Society, \textit{IEEE Standard 802.11: Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications}, IEEE, 2020.

\bibitem{ref_embedded_c}
M. Barr and A. Massa, \textit{Programming Embedded Systems with C and GNU Development Tools}, 2nd ed., O'Reilly Media, 2006.

\bibitem{ref_kalman_filter}
G. Welch and G. Bishop, \textit{An Introduction to the Kalman Filter}, Technical Report TR95-041, University of North Carolina at Chapel Hill, 2006.
\end{thebibliography}
```

---

## Fundamental Typography & Alignment Rules

### 1. Left Alignment & No Content Justification Rule
Do **NOT** use content justification (`\justify` or standard LaTeX paragraph justification). 
- **Rationale**: When line-break hyphenation is disabled (`\hyphenpenalty=10000`), justifying body paragraphs creates uneven, wide spaces between words ("rivering").
- **Implementation**: Enforce left alignment using `\raggedright` for body text and table cells.

```latex
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\emergencystretch=3em
\raggedright
```

### 2. Paragraph Indentation & List Skipping Rule
- **Standard Paragraphs**: `parindent = 0pt` and `parskip = 5pt`.
- **Indentation Rule**: Use paragraph indentation **EXCLUSIVELY** for bullet points, numbered lists, and Roman lists (`\begin{enumerate}[noitemsep,topsep=2pt,parsep=0pt]`). Normal body paragraphs start flush left with a 5pt skip between paragraphs.

---

## Dynamic Multi-Level Heading Scale Algorithm

To calculate exact heading font sizes for any document dynamically, follow this 3-step bottom-up algorithm:

### Step 1: Scan Heading Tree Depth
Scan the actual heading tree depth of the target document:
- Top-level only (Title / Chapter)?
- Top-level + 1 sub-level (Section)?
- Top-level + 2 sub-levels (Section + Subsection)?
- Top-level + 3 sub-levels (Section + Subsection + Sub-subsection)?

*Rule*: **Never assume or reserve a font size for a heading level that is not present in the document.**

### Step 2: Build Bottom-Up from Fixed Body (12pt)
- **Body Text**: Fixed at `12pt` (regular).
- **Deepest Sub-heading present**: `Body + 2pt` = `14pt` (bold).
- **Each level up from there**: `+2pt more` per level.

### Step 3: Apply Top-Level Exception Last
- **Top-Level Heading (Title / Chapter)**: `Direct Child Size + 3pt` (not +2pt).
- **Top-Level Styling**: ALL CAPS, Bold, left-aligned or centered, ended explicitly with `\par`.

---

### Examples of Dynamic Heading Scaling:

#### Example A: Document with Top-Level + 1 Sub-Level Only
- **Body Text**: 12pt (regular)
- **Sub-heading (Level 1)**: 14pt (12 + 2) bold
- **Top-Level (Chapter/Title)**: 17pt (14 + 3) bold, ALL CAPS

#### Example B: Document with Top-Level + 2 Sub-Levels (Standard Report)
- **Body Text**: 12pt (regular)
- **Subsection (Level 2)**: 14pt (12 + 2) bold
- **Section (Level 1)**: 16pt (14 + 2) bold
- **Top-Level (Chapter/Title)**: 19pt or 20pt (16 + 3 or 4) bold, ALL CAPS

#### Example C: Document with Top-Level + 3 Nested Sub-Levels
- **Body Text**: 12pt (regular)
- **Level 3 (1.1.1)**: 14pt (12 + 2) bold
- **Level 2 (1.1)**: 16pt (14 + 2) bold
- **Level 1 (1.)**: 18pt (16 + 2) bold
- **Top-Level Heading**: 21pt (18 + 3) bold, centered/left-aligned, ALL CAPS

---

### Multi-Line Heading Line Spacing Rule

When a long title or heading wraps into 2 or more lines, set `baselineskip` proportionally to **1.2x font size** ended explicitly with `\par`:
- `21pt` font size $\rightarrow$ `\fontsize{21}{26}\selectfont` (21pt / 26pt baseline)
- `20pt` font size $\rightarrow$ `\fontsize{20}{24}\selectfont` (20pt / 24pt baseline)
- `18pt` font size $\rightarrow$ `\fontsize{18}{22}\selectfont` (18pt / 22pt baseline)
- `16pt` font size $\rightarrow$ `\fontsize{16}{20}\selectfont` (16pt / 20pt baseline)
- `15pt` font size $\rightarrow$ `\fontsize{15}{18}\selectfont` (15pt / 18pt baseline)
- `14pt` font size $\rightarrow$ `\fontsize{14}{17}\selectfont` (14pt / 17pt baseline)

This ensures inter-line spacing between wrapped heading lines is comfortable (1.2 line height), never tight or squished.

```latex
\usepackage{titlesec}

% Top-Level Chapter Heading (20pt / 24pt baseline, ALL CAPS)
\titleformat{\chapter}[block]
  {\normalfont\fontsize{20}{24}\selectfont\bfseries\raggedright}
  {\chaptertitlename\ \thechapter\ :}{0.5em}{}
\titlespacing*{\chapter}{0pt}{0pt}{15pt}

% Level 1 Section Heading (15pt / 18pt baseline)
\titleformat{\section}
  {\normalfont\fontsize{15}{18}\selectfont\bfseries\raggedright}
  {\thesection}{1em}{}
\titlespacing*{\section}{0pt}{12pt}{6pt}

% Level 2 Subsection Heading (13pt / 16pt baseline)
\titleformat{\subsection}
  {\normalfont\fontsize{13}{16}\selectfont\bfseries\raggedright}
  {\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{10pt}{4pt}
```

---

## Detailed Component Specifications

### 1. Dynamic Universal Configuration Macros
Every report `.tex` file must feature a central Macro Parameter Configuration Block in the preamble:

```latex
% ==============================================================================
% DYNAMIC UNIVERSAL COLLEGE REPORT CONFIGURATION MACROS
% Replace these values for ANY project, degree, department, or university
% ==============================================================================
\newcommand{\ReportTitle}{TITLE OF YOUR PROJECT OR THESIS HERE}
\newcommand{\ReportType}{Mini Project Report / Capstone / Thesis / Dissertation}
\newcommand{\DegreeName}{Bachelor of Technology / Bachelor of Science / Master of Science}
\newcommand{\BranchName}{Your Specialization / Department Name}
\newcommand{\UniversityName}{Name of Your University}
\newcommand{\CollegeName}{Name of Your College / Institute / Faculty}
\newcommand{\DepartmentName}{Department of ...}
\newcommand{\CollegeLocation}{City, State, Country}
\newcommand{\AcademicYear}{2026}
\newcommand{\SupervisorName}{Dr. / Prof. Supervisor Name}
\newcommand{\SupervisorDesignation}{Project Supervisor / Professor}
\newcommand{\InstitutionLogoPath}{images/logo.png} % Path inside root images/ folder

% Target Page Limit Constraints
\newcommand{\TargetMinPages}{18}
\newcommand{\TargetMaxPages}{22}
```

---

### 2. Chapter New Page Rule
Every chapter **MUST** start on a fresh new page. Place `\clearpage` explicitly before every `\chapter{...}` command:
```latex
\clearpage
\chapter{HARDWARE ARCHITECTURE AND COMPONENT DETAILS}
```

---

### 3. Hyperlink Color Rule: All Black Except Purple Citations

In professional reports, all text elements, URLs, section links, and TOC links must render in **BLACK** (`black`), EXCEPT literature citations which render in **PURPLE** inside brackets:

```latex
% Load hyperref: all links, TOC entries, and URLs strictly black
\usepackage[colorlinks=true, linkcolor=black, citecolor=black, urlcolor=black]{hyperref}

% Citation form: purple italicized numbers inside brackets
\renewcommand{\citeform}[1]{\textcolor{purple}{\itshape #1}}
```

---

### 4. Full-Grid Table Rules

All tables must strictly follow these rules:
1. **Full Grid Borders**: Full grid borders on all cells (`|c|c|`).
2. **Header Row**: Centered horizontally and vertically, rendered in **bold**.
3. **Cell Content**: Left-aligned cell content (no content justification); balance column widths using `C{width}` or `L{width}`.
4. **Row Colors**: NO background row colors or alternating tints (`\rowcolor` prohibited).
5. **Padding & Spacing**: Enforce cell padding using `\renewcommand{\arraystretch}{1.2}` and `\setlength{\tabcolsep}{8pt}`.
6. **Ampersand Match**: Every row must match the column specification count exactly.

```latex
\begin{center}
\begin{tabular}{|C{3.5cm}|C{3.0cm}|C{8.0cm}|}
\hline
\textbf{Parameter / Pin} & \textbf{Value / GPIO} & \textbf{Functional Description} \\ \hline
Data Bus Pin & GPIO 21 & Serial Data Communication Channel \\ \hline
Clock Line Pin & GPIO 22 & Serial Clock Signal Line \\ \hline
\end{tabular}
\vspace{0.05in}
\captionof{table}{System Pinout and Configuration Mapping}
\label{tab:system_pinout_mapping}
\end{center}
```

---

### 5. Inline Code & Dynamic Breakable Code Block Rules

#### A. Inline Code Pill Specification:
Inline code commands (`\code{}`) render in bold monospace with a dark cool-gray background pill `RGB(225,228,233)` for crisp contrast on white pages with `\fboxsep=2.5pt`:

```latex
\definecolor{inlinecodebg}{RGB}{225,228,233}
\newcommand{\code}[1]{{\setlength{\fboxsep}{2.5pt}\colorbox{inlinecodebg}{\small\ttfamily\bfseries#1}}}
```

#### B. Code Block Listing Specification:
Code snippets and firmware listings must be breakable across page boundaries so multi-page code blocks split dynamically without overflowing margins or clipping lines:

1. **Package Combination**: Use `listings` inside `tcolorbox` with `breakable=true`.
2. **Syntax Highlighting**:
   - Background: `RGB(242,244,248)` (Light cool gray tint).
   - Frame Border: `RGB(208,215,222)` (Single line border).
   - Comments: `RGB(106,153,85)` in *italic*.
   - Keywords: `RGB(0,0,255)` in **bold**.
   - Strings: `RGB(163,21,21)`.
3. **Monospace & Line Spacing**: Monospace font at 88% scale (`8.5pt` base, `10.5pt` skip), single line spacing (`\linespread{1.0}`).

```latex
\definecolor{codebg}{RGB}{242,244,248}
\definecolor{codeborder}{RGB}{208,215,222}
\definecolor{codecomment}{RGB}{106,153,85}
\definecolor{codekeyword}{RGB}{0,0,255}
\definecolor{codestring}{RGB}{163,21,21}

\lstset{
  backgroundcolor=\color{codebg},
  commentstyle=\color{codecomment}\itshape,
  keywordstyle=\color{codekeyword}\bfseries,
  stringstyle=\color{codestring},
  basicstyle=\ttfamily\fontsize{8.5}{10.5}\selectfont\linespread{1.0}\selectfont,
  breaklines=true,
  breakatwhitespace=false,
  captionpos=b,
  keepspaces=true,
  numbers=left,
  numberstyle=\tiny\color{gray},
  frame=single,
  rulecolor=\color{codeborder}
}

\begin{tcolorbox}[breakable, colback=codebg, colframe=codeborder, title=Listing X.Y: Module Source Code]
\begin{lstlisting}[language=C++]
// Dynamic breakable source code listing...
\end{lstlisting}
\end{tcolorbox}
```

---

### 6. TikZ Diagram Rules

When drawing vector diagrams or flowcharts using TikZ:
1. **Explicit Library Imports**: Load all required TikZ libraries explicitly in preamble (`\usetikzlibrary{shapes,arrows,positioning}`).
2. **Node Definition**: Define all node styles before use.
3. **Light Fill Tints**: Use light tints ONLY (`myred!10`, `myblue!10`, `black!5`). Never use solid or dark fills at `!50` or above.
4. **Spacing & Labeling**: Ensure proper node spacing and clear text labeling.

## MiKTeX & XeLaTeX Environment Diagnostics & Installation

Before compiling, AI agents and human users **MUST** verify that MiKTeX (or XeLaTeX) is installed on the target machine.

### 1. Environment Diagnostic Command
Run the following PowerShell command to check if `xelatex` is available on the system:
```powershell
Get-Command xelatex -ErrorAction SilentlyContinue | Select-Object Name, Source
xelatex --version
```

### 2. Automatic Installation via `winget` (If Missing)
If `xelatex` is not detected on PATH or in standard user program directories (`%LOCALAPPDATA%\Programs\MiKTeX`), install MiKTeX automatically using Windows Package Manager:

```powershell
winget install --id MiKTeX.MiKTeX --silent --accept-package-agreements --accept-source-agreements
```

### 3. MiKTeX Automatic Package Management
Ensure MiKTeX is set to install missing LaTeX packages on the fly without user prompts:
```powershell
initexmf --set-config-value [MPM]AutoInstall=1
```

---

## Automated Compilation & Verification Workflow

### 1. PowerShell Double-Pass Compiler Script (`compile_xelatex.ps1`)
Run the automated compiler from PowerShell terminal:
```powershell
.\compile_xelatex.ps1
```

The script automatically:
- Detects the primary `.tex` file in the workspace directory.
- Clears stale `.aux`, `.log`, `.toc`, and `.out` files.
- Checks if the target `.pdf` is locked by a viewer.
- Executes two passes of `xelatex -interaction=nonstopmode`.
- Cleans up temporary build artifacts upon successful compilation.

### 2. Final Verification Checklist
Before delivering any report PDF, verify:
- [x] Started from scratch with root `images/` directory and `.tex` source file.
- [x] Analyzed requirements, prompt content, domain engineering, and common sense before building.
- [x] All images stored in root `images/` folder and included via `\graphicspath{{images/}}` or `images/filename.ext`.
- [x] Dynamic captioning and figure numbering set up (`Figure 1.1`, `Table 2.1`) with `\label` placed AFTER `\caption`.
- [x] Every report concludes with mandatory **Conclusion and Future Scope** and **References** chapters.
- [x] Bibliography contains **at least 10 detailed, domain-relevant references** with in-text purple citations (`\cite{...}`).
- [x] Heading scaling algorithm scanned and calculated bottom-up from 12pt body.
- [x] Top-level headings set in ALL CAPS, bold, ended with `\par`.
- [x] Multi-line wrapped headings set proportional baseline skips (1.2x font size) ended with `\par`.
- [x] Body text left-aligned (`\raggedright`), NO content justification used.
- [x] Indentation (`parindent`) used exclusively for bullet points and numbered lists.
- [x] Preamble macro block populated with user/institution details.
- [x] Every chapter starts on a fresh new page (`\clearpage`).
- [x] Global line spacing set to 1.2 (`\setstretch{1.2}`).
- [x] Main font set to Times New Roman (or TeX Gyre Pagella), Monospace set to Courier New @ 88% scale.
- [x] Hyphenation penalties set (`\hyphenpenalty=10000`, `\exhyphenpenalty=10000`).
- [x] Inline code pills use `RGB(225,228,233)` background with `\fboxsep=2.5pt`.
- [x] All links, text, and headings are strictly **BLACK** (`black`), except citations which are **PURPLE**.
- [x] Tables follow full-grid (`|c|c|`) rules with left-aligned cells and centered bold headers.
- [x] Code blocks wrapped in `tcolorbox` with `breakable=true`.
- [x] No personal/corporate branding present in headers or footers.
- [x] Final page count falls strictly within institution page budget (e.g. \TargetMinPages–\TargetMaxPages\ pages).
