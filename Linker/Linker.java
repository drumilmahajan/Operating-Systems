import java.util.*;
import java.util.Scanner;
import java.io.*;

/*
 * Created by Drumil Mahajan
 * Linker
 * Operating Systems, Independent Project, Fall 2016
 */

public class Linker {

    public static HashMap<String, Integer> symbolTable = new HashMap<String, Integer>();
    public static HashMap<String, String> symbolUsedBool = new HashMap<String, String>();
    public static HashMap<String, Integer> symbolModNum = new HashMap<String, Integer>();
    public static HashMap<String, String> symUsedHash;
    public static ArrayList<String> warnings = new ArrayList<String>();
    public static int numModule = 0;
    public static int memSize = 0; 
        

    //public static

    /*
    Pass one determines the base
    address for each module and the absolute address for each external symbol, storing the later in the symbol
    table it produces. The first module has base address zero; the base address for module I+1 is equal to the
    base address of module I plus the length of module I. The absolute address for a relative address defined in
    module M is the base address of M plus the relative address of S within M.
     */
    public static int[] passOne(Scanner file, int numModules) {



        int numSymbols = 0;
        int symVal = 0;
        String symName = "";
        int[] moduleBaseAdd = new int[numModules];
        int[] moduleLengthArr = new int[numModules];

        moduleBaseAdd[0] = 0; // Base Address of first module is 0.

        System.out.println("");

        for(int i = 0; i < numModules; i++){
            numSymbols = file.nextInt();
            for(int j = 0; j < numSymbols; j++){
                
                symName = file.next();
                
                symVal = file.nextInt() + moduleBaseAdd[i];
                if(!symbolTable.containsKey(symName)) {
                    symbolTable.put(symName, symVal);
                    symbolUsedBool.put(symName , "False" ); 
                    symbolModNum.put(symName, i);
                }
                else
                    System.out.println(symName + " was defined multiply. Value will be used from its first definition.");

            }
            int numUse = file.nextInt();
            for(int k = 0; k < numUse; k++){
                file.next();
            }
            int numDir = file.nextInt();
            if(i<moduleBaseAdd.length - 1)
                moduleBaseAdd[i+1] = moduleBaseAdd[i] + numDir; // Calculating base address for number of modules.
            moduleLengthArr[i] = numDir;
            //for(int h = 0 ; h < 4 ; h++ )
            //System.out.println(moduleLengthArr[i]);
            for(int k = 0; k < numDir; k++ ){
                file.next();
            }
            if(i == numModule - 1){   // Calculating the number of memory.
                memSize = moduleBaseAdd[i] + numDir;
                //System.out.println("Mem size  ++++++++++++++++++++ " + memSize);
            }    
        }

        System.out.println(""); 
        System.out.println("Symbol Table");
        

        for(String symbolName : symbolTable.keySet()){
            String key = symbolName;
            int value = symbolTable.get(symbolName);
            if( value > memSize) {
                int baseAddress = 0;
                int moduleNumber = symbolModNum.get(key);
                baseAddress = moduleBaseAdd[moduleNumber];
                symbolTable.put(key , baseAddress);
                value = symbolTable.get(symbolName);
            }
            System.out.println(key + " = " + value);
        }
        return moduleLengthArr;
    }

    /*
    Pass two uses the base addresses
    and the symbol table computed in pass one to generate the actual output by relocating relative addresses
    and resolving external references.
     */
    public static void passTwo(Scanner file, int numModules, int[] moduleLengthArr) {


        System.out.println("\nMemory Map");

        int numSym = 0;
        int numUses = 0;
        int numDir = 0;
        int address = 0;
        int addType = 0;
        int memory = 0;
        String symUsed = "";
        int[] baseAddArray = new int[numModules];
        ArrayList<Integer> Address = new ArrayList<Integer>();

        // Creating Base Address Array from module length Array 
        baseAddArray[0] = 0; // Base address of module 1 is 0; 
        for( int i = 1; i < numModules ; i++){
            baseAddArray[i] = moduleLengthArr[i-1] + baseAddArray [i - 1];
        }

        for(int num = 0; num < numModules; num++) {
            numSym = file.nextInt();
            for (int i = 0; i < numSym; i++) {
                file.next();
                file.nextInt();
            }
            numUses = file.nextInt();
            String[] symbolUsed = new String[numUses];
            symUsedHash = new HashMap<String ,String>();
            for (int i = 0; i < numUses; i++) {
                symUsed = file.next();
                if( symbolUsedBool.containsKey(symUsed))
                    symbolUsedBool.put(symUsed , "True");
                //System.out.println(symUsed);
                symbolUsed[i] = symUsed;
                symUsedHash.put(symUsed, "False");    
            }
            numDir = file.nextInt();
            //System.out.println(numDir);
            for (int i = 0; i < numDir; i++) {
                
                address = file.nextInt();
                addType = address % 10;
                //System.out.println(addType);
                address = address / 10;

                if (addType == 1) {
                    System.out.println(memory + ":  " + address);
                    memory++;
                    Address.add(address);
                }

                else if (addType == 2) {
                    if(address % 1000 > 600){
                        address = address - address%1000;  // Using zero instead 
                        System.out.print(memory + ":  " + address + "  ");
                        memory++;
                        Address.add(address);
                        System.out.println("Error: Absolute address exceeds machine size; zero used.");        
                    }
                    else{
                        System.out.println(memory + ":  " + address + "  ");
                        memory++;
                        Address.add(address);
                    }    
                }

                else if (addType == 3) {
                    int exceptionRaised = 0;
                    int baseAdd = 0;

                    baseAdd = address % 1000; 

                    if(baseAdd > moduleLengthArr[num]){
                        address = address - baseAdd;
                        System.out.print(memory + ":  " + address + "  ");
                        memory++;  
                        System.out.println("Error: Relative address exceeds module size; zero used.");

                    }

                    else {
                        address = address + baseAddArray[num];
                        System.out.println(memory + ":  " + address + "  ");
                        memory++;    
                        Address.add(address);
                    }                   
                } 

                else if (addType == 4) {
                    int exceptionRaised = 0;
                    int useIndex = address % 10;
                    String usedSym = "";
                    try{
                        usedSym = symbolUsed[useIndex];
                    }
                    catch(ArrayIndexOutOfBoundsException exception){
                        
                        exceptionRaised = 1;
                    }

                    if(exceptionRaised == 0){

                        address = address - address % 1000;
                        if(symbolTable.containsKey(usedSym)){
                            symUsedHash.put(usedSym , "True");   
                            address = address + symbolTable.get(usedSym);
                            System.out.println(memory + ":  " + address + "  ");
                            memory++;
                            Address.add(address); 
                        }
                        else{
                            symUsedHash.put(usedSym , "ND");
                            address = address + 0; // Using the default value as 0
                            System.out.print(memory + ":  " + address + "  ");
                            memory++;
                            System.out.println("Error: " + usedSym +" is not defined; zero used.");
                    }
                    }
                    else if(exceptionRaised == 1){
                        System.out.print(memory + ":  " + address + "  ");
                        memory++;
                        System.out.println("Error: External address exceeds length of use list; treated as immediate.");
                        Address.add(address);
                        exceptionRaised = 0;
                    }
                } else
                    System.out.println("Undefined Addressing");

            } 
            
            for(String symbolName : symUsedHash.keySet()) {
                String sym = symbolName;
                String value = symUsedHash.get(symbolName);
                if( value == "False" ) {
                    warnings.add("WARNING : Symbol " + sym + " mentioned in module " + num + " in use list but not actually used. ");
                }
            }
        }

            for(int i = 0; i < Address.size(); i++){
              // System.out.println("" + Address.get(i));
            }

            // Print WARNING Messages 
            System.out.println("\n");
            for(String symbolName : symbolUsedBool.keySet() ){
                String key = symbolName;
                String value = symbolUsedBool.get(symbolName);
                int symbolModulenumber = symbolModNum.get(symbolName);
                if( value == "False") {
                    System.out.println("WARNING : Symbol " + key + " defined in module number " + symbolModulenumber + " but not used.");    
                }
            }

            for(int i = 0; i < warnings.size(); i++) {
                System.out.println(warnings.get(i));
            }
        }


    public static void main(String args[]) throws FileNotFoundException {

        String fileName = args[0];
        Scanner input = new Scanner(new File(fileName));
        int[] moduleLengths = new int[numModule];
        numModule = input.nextInt();
        moduleLengths = passOne(input, numModule);


        input = new Scanner(new File(fileName));
        numModule = input.nextInt();
        passTwo(input, numModule, moduleLengths);

    }

}