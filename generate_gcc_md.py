import yaml
from jinja2 import Environment, FileSystemLoader
import os
import argparse
from pathlib import Path

def format_value(value):
    if isinstance(value, str):
        if value.startswith('0b'):
            return value
        elif value.startswith('0x'):
            return bin(int(value, 16))
        else:
            try:
                return bin(int(value))
            except:
                return value
    elif isinstance(value, int):
        return bin(value)
    else:
        return value

def parse_inst(yaml_path):
    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        name = data.get("name", "unknown")
        long_name = data.get("long_name", "")
        description = data.get("description", "").strip().replace("\n", " ")
        
        assembly = data.get("assembly", "")
        if isinstance(assembly, str):
            operands = [op.strip() for op in assembly.split(",") if op.strip()]
        else:
            operands = ["rd", "rs1", "rs2"]
        
        format_data = data.get("format", {})
        
        opcodes = format_data.get("opcodes", {})
        
        opcode_data = opcodes.get("opcode", {})
        if isinstance(opcode_data, dict) and "$inherits" in opcode_data:
            opcode = "0b0110011"
        else:
            opcode = opcode_data.get("value", "0b0110011")
        
        funct3_data = opcodes.get("funct3", {})
        funct3_raw = funct3_data.get("value") if isinstance(funct3_data, dict) else None
        funct3 = format_value(funct3_raw) if funct3_raw else None
        
        funct7_data = opcodes.get("funct7", {})
        funct7_raw = funct7_data.get("value") if isinstance(funct7_data, dict) else None
        funct7 = format_value(funct7_raw) if funct7_raw else None
        
        gcc_operands = convert_to_gcc(operands)
        
        instr_type = determine_inst_type(name, operands, funct7, funct3)
        
        return {
            "name": name.lower(),
            "long_name": long_name,
            "description": description,
            "operands": operands,
            "gcc_operands": gcc_operands,
            "opcode": opcode,
            "funct3": funct3,
            "funct7": funct7,
            "instruction_type": instr_type,
            "constraint_string": generate_string(operands)
        }
        
    except Exception as e:
        print(f"Error parsing {yaml_path}: {e}")
        return None

def convert_to_gcc(operands):
    gcc_ops = []
    for i, op in enumerate(operands):
        if op.startswith('x') and (op[1:].isdigit() or op[1:] in ['d', 's1', 's2']):
            constraint = "=r" if i == 0 else "r"
            gcc_ops.append(f'(match_operand:SI {i} "register_operand" "{constraint}")')
        else:
            constraint = "=r" if i == 0 else "r"
            gcc_ops.append(f'(match_operand:SI {i} "register_operand" "{constraint}")')
    
    return gcc_ops

def determine_inst_type(name, operands, funct7, funct3):
    name_lower = name.lower()
    
    if any(x in name_lower for x in ['add', 'sub', 'and', 'or', 'xor']):
        return "arith"
    elif any(x in name_lower for x in ['sll', 'srl', 'sra', 'rol', 'ror']):
        return "shift"
    elif any(x in name_lower for x in ['mul', 'div']):
        return "imul"
    elif any(x in name_lower for x in ['load', 'ld']):
        return "load"
    elif any(x in name_lower for x in ['store', 'st']):
        return "store"
    else:
        return "arith"

def generate_string(operands):
    constraints = []
    for i, op in enumerate(operands):
        if i == 0:
            constraints.append("=r")
        else:
            constraints.append("r")
    
    return '", "'.join(constraints)

def generate_md(folder_path, template_path, out_file):
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    
    instructions = []
    
    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".yaml"):
            continue
            
        full_path = os.path.join(folder_path, file_name)
        instr = parse_inst(full_path)
        
        if instr:
            instructions.append(instr)
            print(f"Parsed: {instr['name']}")
        else:
            print(f"Failed to parse: {file_name}")
    
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    
    with open(out_file, 'w') as out:
        out.write(";; Generated RISC-V GCC Machine Description\n")
        out.write(";; Auto-generated from RISC-V UDB YAML specifications\n")
        out.write(";; Do not modify manually\n\n")
        
        for instr in instructions:
            rendered = template.render(**instr)
            out.write(rendered)
            out.write("\n\n")
    
    print(f"✅ Generated {len(instructions)} instructions in '{out_file}'")

def main():
    parser = argparse.ArgumentParser(description='Convert RISC-V UDB YAML to GCC .md files')
    parser.add_argument('--udb_path', required=True, help='Path to UDB YAML file or directory')
    parser.add_argument('--output_dir', required=True, help='Output directory for .md files')
    parser.add_argument('--template', default='templates/instruction.md.j2', 
                       help='Path to Jinja2 template file')
    
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    udb_path = Path(args.udb_path)
    
    if udb_path.is_file():
        out_file = os.path.join(args.output_dir, f"{udb_path.stem}.md")
        
        temp_dir = "temp_udb"
        os.makedirs(temp_dir, exist_ok=True)
        
        import shutil
        shutil.copy2(args.udb_path, temp_dir)
        
        generate_md(temp_dir, args.template, out_file)
        
        shutil.rmtree(temp_dir)
        
    elif udb_path.is_dir():
        out_file = os.path.join(args.output_dir, "riscv_generated.md")
        generate_md(args.udb_path, args.template, out_file)
    else:
        print(f"Error: {args.udb_path} is not a valid file or directory")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())