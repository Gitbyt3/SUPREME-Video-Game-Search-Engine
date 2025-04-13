export type Genre = 'Adventure' | 'Arcade' | 'Brawler' | 'Card & Board Game' | 'Fighting' |
       'Indie' | 'MOBA' | 'Music' | 'Pinball' | 'Platform' | 'Point-and-Click' |
       'Puzzle' | 'Quiz/Trivia' | 'RPG' | 'Racing' | 'Real Time Strategy' |
       'Shooter' | 'Simulator' | 'Sport' | 'Strategy' | 'Tactical' |
       'Turn Based Strategy' | 'Visual Novel';

const originalSize = {width: 1536, height: 1024, iconSize: 220}
const spriteMap = {
    'Adventure': { x: -60, y: -48 },
    'Arcade': { x: -280, y: -48 },
    'Brawler': { x: -500, y: -48 },
    'Card & Board Game': { x: -750, y: -48 },
    'Fighting': { x: -995, y: -48 },
    'Indie': { x: -1255, y: -48 },
    'MOBA': { x: -60, y: -300 },
    'Music': { x: -285, y: -300 },
    'Pinball': { x: -510, y: -300 },
    'Platform': { x: -740, y: -310 },
    'Point-and-Click': { x: -1000, y: -300 },
    'Puzzle': { x: -1260, y: -300 },
    'Quiz/Trivia': { x: -70, y: -542 },
    'RPG': { x: -282, y: -542 },
    'Racing': { x: -505, y: -548 },
    'Real Time Strategy': { x: -750, y: -538 },
    'Shooter': { x: -1010, y: -552 },
    'Simulator': { x: -1265, y: -550 },
    'Sport': { x: -60, y: -774 },
    'Strategy': { x: -284, y: -774 },
    'Tactical': { x: -510, y: -772 },
    'Turn Based Strategy': { x: -1005, y: -758 },
    'Visual Novel': { x: -1260, y: -772 },
}

export const GenreIcon: React.FC<{ genre: Genre, size: number }> = ({ genre, size }) => {
  if (!genre) genre = 'Adventure';
  const sizeRatio = size / originalSize.iconSize;
  return (
    <div className="genre-icon" style={{ width: size, height: size, backgroundPosition: `${sizeRatio * spriteMap[genre].x}px ${sizeRatio * spriteMap[genre].y}px`, backgroundImage: `url(./assets/genres.png)`, backgroundRepeat: 'no-repeat', backgroundSize: `${sizeRatio * originalSize.width}px ${sizeRatio * originalSize.height}px` }}>
    </div>
  );
};
