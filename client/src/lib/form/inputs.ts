type EnumData = {
	type: 'enum';
	values: string[];
}

type InputNumber = {
	type: 'number';
}

type InputString = {
	type: 'string'
}

type InputData = EnumData | InputNumber | InputString;

type InputField = {
	description: string;
	data: InputData;
}

type Form = {
	title: string,
	inputs: InputField[]
}

export type { InputField, InputData, EnumData, Form }

const inputIssues = (input: InputField, id: string): string[] => {
	let issues = [];
	if (input.description.length === 0) {
		issues.push(id + ': Description is required');	
	}
	switch (input.data.type) {
		case 'enum':
			if (input.data.values.length === 0) {
				issues.push(id + ': Enum values are required');
			}
			break;
	}
	return issues;
}

export { inputIssues }
