"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const recordCtrController_1 = require("../controllers/recordCtrController");
const router = (0, express_1.Router)();
router.get('/', recordCtrController_1.handleRecordCtr);
exports.default = router;
