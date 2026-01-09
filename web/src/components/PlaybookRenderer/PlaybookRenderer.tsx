import styles from './PlaybookRenderer.module.css';

interface ParsedBullet {
  id: string;
  helpful: number;
  harmful: number;
  content: string;
}

interface ParsedSection {
  title: string;
  bullets: ParsedBullet[];
  rawContent: string[];
}

function parseBulletLine(line: string): ParsedBullet | null {
  // Pattern: [id] helpful=X harmful=Y :: content
  const pattern = /^\[([^\]]+)\]\s*helpful=(\d+)\s*harmful=(\d+)\s*::\s*(.*)$/;
  const match = line.trim().match(pattern);

  if (match) {
    return {
      id: match[1],
      helpful: parseInt(match[2], 10),
      harmful: parseInt(match[3], 10),
      content: match[4],
    };
  }
  return null;
}

function parsePlaybook(content: string): ParsedSection[] {
  // Handle escaped newlines
  const normalizedContent = content.replace(/\\n/g, '\n');
  const lines = normalizedContent.split('\n');

  const sections: ParsedSection[] = [];
  let currentSection: ParsedSection = {
    title: '',
    bullets: [],
    rawContent: [],
  };

  for (const line of lines) {
    const trimmedLine = line.trim();

    // Check for section header (## Header)
    if (trimmedLine.startsWith('## ')) {
      // Save previous section if it has content
      if (currentSection.title || currentSection.bullets.length > 0 || currentSection.rawContent.length > 0) {
        sections.push(currentSection);
      }
      currentSection = {
        title: trimmedLine.slice(3).trim(),
        bullets: [],
        rawContent: [],
      };
    }
    // Check for main title (# Title)
    else if (trimmedLine.startsWith('# ') && !trimmedLine.startsWith('## ')) {
      if (currentSection.title || currentSection.bullets.length > 0 || currentSection.rawContent.length > 0) {
        sections.push(currentSection);
      }
      currentSection = {
        title: trimmedLine.slice(2).trim(),
        bullets: [],
        rawContent: [],
      };
    }
    // Check for ACE bullet format
    else if (trimmedLine.startsWith('[')) {
      const bullet = parseBulletLine(trimmedLine);
      if (bullet) {
        currentSection.bullets.push(bullet);
      } else {
        // Not a valid bullet, treat as raw content
        if (trimmedLine) {
          currentSection.rawContent.push(trimmedLine);
        }
      }
    }
    // Regular content (markdown list items, paragraphs, etc.)
    else if (trimmedLine) {
      currentSection.rawContent.push(trimmedLine);
    }
  }

  // Add the last section
  if (currentSection.title || currentSection.bullets.length > 0 || currentSection.rawContent.length > 0) {
    sections.push(currentSection);
  }

  return sections;
}

function BulletCard({ bullet }: { bullet: ParsedBullet }) {
  const score = bullet.helpful - bullet.harmful;
  const scoreClass = score > 0 ? styles.scorePositive : score < 0 ? styles.scoreNegative : styles.scoreNeutral;

  return (
    <div className={styles.bulletCard}>
      <div className={styles.bulletHeader}>
        <span className={styles.bulletId}>{bullet.id}</span>
        <div className={styles.scores}>
          <span className={styles.helpful} title="Helpful count">
            <span className={styles.scoreIcon}>↑</span>
            {bullet.helpful}
          </span>
          <span className={styles.harmful} title="Harmful count">
            <span className={styles.scoreIcon}>↓</span>
            {bullet.harmful}
          </span>
          <span className={`${styles.netScore} ${scoreClass}`} title="Net score">
            {score >= 0 ? '+' : ''}{score}
          </span>
        </div>
      </div>
      <div className={styles.bulletContent}>{bullet.content}</div>
    </div>
  );
}

function RawContentRenderer({ lines }: { lines: string[] }) {
  if (lines.length === 0) return null;

  return (
    <div className={styles.rawContent}>
      {lines.map((line, index) => {
        // Handle markdown-style list items
        if (line.startsWith('- ') || line.startsWith('* ')) {
          return (
            <div key={index} className={styles.listItem}>
              <span className={styles.listBullet}>•</span>
              <span>{line.slice(2)}</span>
            </div>
          );
        }
        return <p key={index}>{line}</p>;
      })}
    </div>
  );
}

interface PlaybookRendererProps {
  content: string;
}

export function PlaybookRenderer({ content }: PlaybookRendererProps) {
  const sections = parsePlaybook(content);

  if (sections.length === 0) {
    return <div className={styles.empty}>No content</div>;
  }

  return (
    <div className={styles.playbook}>
      {sections.map((section, sectionIndex) => (
        <div key={sectionIndex} className={styles.section}>
          {section.title && (
            <h3 className={styles.sectionTitle}>{section.title}</h3>
          )}

          {section.rawContent.length > 0 && (
            <RawContentRenderer lines={section.rawContent} />
          )}

          {section.bullets.length > 0 && (
            <div className={styles.bulletsList}>
              {section.bullets.map((bullet) => (
                <BulletCard key={bullet.id} bullet={bullet} />
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
