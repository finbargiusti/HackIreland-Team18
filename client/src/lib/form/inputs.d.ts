type EnumData = {
	type: 'enum';
	values: string[];
}

type InputRange = {
	type: 'range';
	min: number;
	max: number;
}

type InputString = {
	type: 'string';
	value: string;
}

type InputDate = {
	type: 'date';
	value: Date;
}

type InputNumber = {
	type: 'number';
	value: number;
}

type InputBoolean = {
	type: 'boolean';
	value: boolean;
}

type InputData = EnumData ;//| InputRange | InputString | InputDate | InputNumber | InputBoolean;

type InputField = {
	description: string;
	data: InputData;
}

type Form = {
	title: string,
	inputs: InputField[]
}

export type { InputField, InputData, EnumData, Form }
