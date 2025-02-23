type InputChoice = {
	type: 'choice';
	values: string[];
}

type InputNumber = {
	type: 'number';
}

type InputString = {
	type: 'string'
}

type InputData = InputChoice | InputNumber | InputString;

type InputField = {
	description: string;
	data: InputData;
	label: string;
}

type Result = {
	date: string,
	email: string,
	form_id: string,
	admin_id: string,
	[key: string]: string
}

type Form = {
	title: string,
	inputs: InputField[]
	users: string[]
	results: Result[]
}

export type { InputField, InputData, InputChoice, Form, Result }

const inputIssues = (input: InputField, id: string): string[] => {
	let issues = [];
	if (input.description.length === 0) {
		issues.push(id + ': Description is required');	
	}
	if (input.label.length === 0) {
		issues.push(id + ': Label is required');
	}
	switch (input.data.type) {
		case 'choice':
			if (input.data.values.length === 0) {
				issues.push(id + ': Choices are required');
			}
			break;
	}
	return issues;
}

export { inputIssues }
