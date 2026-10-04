type ColorStyle = { background: string; color: string }

const COLOR_STYLES: Record<string, ColorStyle> = {
  // Bières
  Blanche: { background: '#efe3c8', color: '#7a6240' },
  Blonde: { background: '#f3d97a', color: '#6e5304' },
  Ambrée: { background: '#eeb978', color: '#744511' },
  Brune: { background: '#c9ad96', color: '#4f3220' },
  Fruitée: { background: '#d9c0e8', color: '#5f3478' },

  // Vins
  Blanc: { background: '#f1e9b5', color: '#756a1c' },
  Rosé: { background: '#f5b9c8', color: '#8c2c49' },
  Rouge: { background: '#e0959c', color: '#6e1a25' },
}

const DEFAULT_COLOR_STYLE: ColorStyle = { background: '#d1d5db', color: '#374151' }

export const getColorStyle = (color: string): ColorStyle =>
  COLOR_STYLES[color] ?? DEFAULT_COLOR_STYLE
