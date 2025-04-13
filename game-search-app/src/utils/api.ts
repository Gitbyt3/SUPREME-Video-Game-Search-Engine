function handleError(data: any) {
  if (data.hasError) {
    alert(data.message);
    throw new Error(data.message);
  }
}
export const query = async (q: string) => 
  (await fetch('http://localhost:3005/search?keywords=' + encodeURIComponent(q)))
    .json()
    .then((data) => {
      handleError(data);
      data.map((item: any) => {
        const jsonFields = ['developers', 'platforms', 'genres'];
        for(let value of jsonFields) {
            item[value] = JSON.parse(item[value]);
        }

        item['bm25Score'] = item['BM25 Score'];
        item['bm25Scores'] = item['BM25_Scores'] || [];
        item['sbertScore'] = item['SBERT Score'];

        const date = new Date(item['release_date']);
        if (isNaN(date.valueOf())) {
          item['releaseYear'] = item['release_date'] || '-';
        } else {
          item['releaseYear'] = date.getFullYear()
        }

        return item;
      });

      return data;
    })

export const recordCtr = async(id: string | number) =>
  (await fetch('http://localhost:3005/record_ctr?id=' + id))