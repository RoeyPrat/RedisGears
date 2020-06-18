package gears.operations;

import java.io.Serializable;

import gears.records.BaseRecord;

public interface AccumulateOperation<I extends Serializable, R extends Serializable> extends Serializable {

	public R accumulate(R accumulator, I record) throws Exception;
	
}
