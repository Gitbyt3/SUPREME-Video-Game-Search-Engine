"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.init = init;
const node_child_process_1 = __importDefault(require("node:child_process"));
const node_path_1 = __importDefault(require("node:path"));
let retrieve = {
    irProcess: undefined
};
exports.default = retrieve;
function init() {
    const irPath = node_path_1.default.resolve(process.cwd(), '../MODULES/main.py');
    console.log('calling', 'python', irPath);
    const _irProcess = node_child_process_1.default.spawn('python', ['-u', irPath], {
        cwd: node_path_1.default.resolve(process.cwd(), '..'),
        stdio: ['pipe', 'pipe', 'pipe']
    });
    _irProcess.stdout.on('data', function listener(data) {
        data = data.toString();
        if (data === 'initialized') {
            console.log('IR process initialized');
            _irProcess.stdout.off('data', listener);
            retrieve.irProcess = _irProcess;
        }
        if (!retrieve.irProcess) {
            console.log('Message from IR process:', data);
        }
    });
    _irProcess.stderr.on('data', (data) => {
        console.error(data.toString());
    });
    return _irProcess;
}
