//This file was generated from (Academic) UPPAAL 4.1.13 (rev. 5160), November 2012

/*

*/
A[] (((not (mTarget.L6) || not (mTarget.data == INVALID)) || mTarget.cmd == writeCmd) || (not (mTarget.L6) || not (mTarget.data != INVALID)) || mTarget.cmd == readCmd)

/*

*/
A[] (((not (Init.L5) || not (Init.current.cmd == writeCmd)) || Init.SentData == mTarget.RcvdData) || (not (Init.L5) || not (Init.current.cmd == readCmd)) || Init.RcvdData == mTarget.SentData)

/*

*/
A[] Init.SentData == mTarget.RcvdData

/*

*/
Init.L1 --> (Init.L4 and x>=delay1)

/*

*/
Init.L1 --> (Init.L2 or Init.L3)

/*

*/
(Init.L2 or Init.L3) -->  Init.L1

/*

*/
A[]  not deadlock\

