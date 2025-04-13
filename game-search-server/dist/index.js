"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const search_1 = __importDefault(require("./routes/search"));
const recordCtr_1 = __importDefault(require("./routes/recordCtr"));
const retrieve_1 = require("./service/retrieve");
const cors_1 = __importDefault(require("cors"));
const app = (0, express_1.default)();
const port = 3005;
// Use CORS middleware
app.use((0, cors_1.default)());
// Use routes
app.use('/search', search_1.default);
app.use('/record_ctr', recordCtr_1.default);
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
// establish python service
console.log('Establishing IR service');
(0, retrieve_1.init)();
