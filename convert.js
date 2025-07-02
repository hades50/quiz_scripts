const fs = require('fs');
const path = require('path');

async function convertMarkdownToJson(filePath) {
    const fileName = path.basename(filePath);
    const fileContent = fs.readFileSync(filePath, 'utf8');
    const lines = fileContent.split('\n').map(line => line.trim()).filter(line => line.length > 0);

    const questions = [];
    let currentQuestion = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];

        // Check for a new question
        if (line.startsWith('####')) {
            if (currentQuestion) {
                questions.push(currentQuestion); // Save previous question if exists
            }
            currentQuestion = {
                question: line.substring(4).trim(),
                picture_url: '',
                correct_answer: -1, // Will be set based on options
                options: []
            };
            continue; // Move to the next line
        }

        if (!currentQuestion) {
            continue; // Skip lines until a question is found
        }

        // Check for picture URL
        const imageMatch = line.match(/!\[.*\]\((.*)\)/);
        if (imageMatch && imageMatch[1]) {
            currentQuestion.picture_url = imageMatch[1];
            continue;
        }

        // Check for options
        const optionMatch = line.match(/\[(x| )\]\s*(.*)/);
        if (optionMatch) {
            const isCorrect = optionMatch[1] === 'x';
            const optionText = optionMatch[2].trim();

            currentQuestion.options.push({
                option_text: optionText,
                is_correct: isCorrect
            });

            if (isCorrect) {
                currentQuestion.correct_answer = currentQuestion.options.length - 1;
            }
        }
    }

    // Push the last question if it exists
    if (currentQuestion) {
        questions.push(currentQuestion);
    }

    // Get last modified date
    const stats = await fs.promises.stat(filePath);
    const updatedDate = stats.mtime; // Modification time

    return {
        name_of_markdown: fileName,
        questions: questions.map(q => ({
            question: q.question,
            picture_url: q.picture_url,
            correct_answer: q.correct_answer,
            options: q.options,
            updated_at: updatedDate.toISOString() // Convert to ISO string for JSON
        }))
    };
}

// Example Usage:
// node markdownToJson.js <your_markdown_file.md>
if (process.argv.length < 3) {
    console.log('Usage: node markdownToJson.js <path_to_markdown_file.md>');
    process.exit(1);
}

const markdownFilePath = process.argv[2];

convertMarkdownToJson(markdownFilePath)
    .then(jsonData => {
        const outputFileName = path.basename(markdownFilePath, '.md') + '.json';
        fs.writeFileSync(outputFileName, JSON.stringify(jsonData, null, 2), 'utf8');
        console.log(`Successfully converted "${markdownFilePath}" to "${outputFileName}"`);
    })
    .catch(error => {
        console.error('Error:', error.message);
    });
