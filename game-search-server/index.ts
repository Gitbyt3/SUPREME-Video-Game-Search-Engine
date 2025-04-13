import express from 'express';
import searchRoutes from './routes/search';
import recordCtrRoutes from './routes/recordCtr';
import { init as initIRService } from './service/retrieve';
import cors from 'cors';

const app = express();
const port = 3005;

// Use CORS middleware
app.use(cors());

// Use routes
app.use('/search', searchRoutes);
app.use('/record_ctr', recordCtrRoutes);

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
}); 

// establish python service
console.log('Establishing IR service');
initIRService();
