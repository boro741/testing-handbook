import React, {type ReactNode} from 'react';
import styles from './styles.module.css';

// Highlighted summary box used at the top of every chapter: <TLDR>...</TLDR>
export default function TLDR({children}: {children: ReactNode}): React.ReactElement {
  return (
    <div className={styles.tldr} role="note" aria-label="TL;DR">
      <strong className={styles.label}>TL;DR</strong>
      <div>{children}</div>
    </div>
  );
}
