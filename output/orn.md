;; Generated RISC-V GCC Machine Description
;; Auto-generated from RISC-V UDB YAML specifications
;; Do not modify manually

;; orn: Performs the bitwise logical OR operation between xs1 and the bitwise inversion of xs2.
;; Long name: OR with inverted operand
;; funct7: 0b100000
;; funct3: 0b110
;; opcode: 0b0110011

(define_insn "orn"
  [(set (match_operand:SI 0 "register_operand" "=r")
        (ior:SI (match_operand:SI 1 "register_operand" "r")
                    (not:SI (match_operand:SI 2 "register_operand" "r"))))]
  "TARGET_ZBB || TARGET_ZBKB"
  "orn\t%0,%1,%2"
  [(set_attr "type" "arith")
   (set_attr "mode" "SI")])

