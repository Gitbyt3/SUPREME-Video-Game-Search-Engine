"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleSearch = void 0;
const paramValidator_1 = require("../utils/paramValidator");
const retrieve_1 = __importDefault(require("../service/retrieve"));
const sqlite3_1 = __importDefault(require("sqlite3"));
const databaseService_1 = __importDefault(require("../service/databaseService"));
const handleSearch = (req, res) => {
    if (!(0, paramValidator_1.validateParams)(req, res, ['keywords']))
        return;
    const keywords = req.query.keywords;
    console.log(req.query.ltr);
    const useLTR = req.query.ltr === '1';
    if (!retrieve_1.default.irProcess) {
        res.json({
            hasError: true,
            message: 'Server has not initialized...'
        });
        return;
    }
    const reqId = `${Math.random()}`;
    const message = JSON.stringify({
        id: reqId,
        query: keywords,
        useLTR
    });
    retrieve_1.default.irProcess.stdin.write(message);
    retrieve_1.default.irProcess.stdin.write('\n');
    console.log('Message sent to IR process', message);
    retrieve_1.default.irProcess.stdout.on('data', function listener(data) {
        var _a, _b;
        console.log('Got message from IR process:', data.toString());
        console.log('Expecting ID:', reqId);
        try {
            data = JSON.parse(data.toString());
            if (data.id === reqId) {
                (_a = retrieve_1.default.irProcess) === null || _a === void 0 ? void 0 : _a.stdout.off('data', listener);
                // Connect to the SQLite database
                const db = new sqlite3_1.default.Database('./games.db', sqlite3_1.default.OPEN_READONLY, (err) => {
                    if (err) {
                        console.error('Error opening database:', err.message);
                        res.json({ hasError: true, message: 'Database error' });
                        return;
                    }
                });
                // Query the database and merge results
                const ids = data.data.map((item) => item.ID);
                const placeholders = ids.map(() => '?').join(',');
                const query = `SELECT * FROM games WHERE id IN (${placeholders})`;
                databaseService_1.default.query(query, ids)
                    .then(rows => {
                    // Merge database rows with data.data
                    const mergedData = data.data.map((item) => {
                        const dbRow = rows.find((row) => row.id === item.ID);
                        if (typeof item === 'object' && item !== null && typeof dbRow === 'object' && dbRow !== null) {
                            return Object.assign(Object.assign({}, item), dbRow);
                        }
                        return item; // Return the original item if merging is not possible
                    });
                    res.json(mergedData);
                })
                    .catch(err => {
                    console.error('Error querying database:', err.message);
                    res.json({ hasError: true, message: 'Database query error' });
                });
                return;
            }
        }
        catch (ex) {
            console.error(ex);
            (_b = retrieve_1.default.irProcess) === null || _b === void 0 ? void 0 : _b.stdout.off('data', listener);
            res.json({ hasError: true });
        }
    });
};
exports.handleSearch = handleSearch;
