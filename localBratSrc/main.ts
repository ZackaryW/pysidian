import { Plugin } from 'obsidian';

export default class LocalBrat extends Plugin {
    async onload() {
        console.log('LocalBrat has been loaded');
    }

    onunload() {
        console.log('LocalBrat has been unloaded');
    }
}
