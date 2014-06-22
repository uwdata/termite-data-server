var CoreModel = Backbone.Model.extend();

CoreModel.prototype.triggerDirty = function() {
	this.trigger( "dirty", this.__dirty__ || {} );
	delete this.__dirty__;
};

CoreModel.prototype.__combineDirty__ = function( dirty, otherDirty ) {
	if ( dirty === true || otherDirty === true )
		return true;
	for ( key in otherDirty )
		if ( Array.isArray( key ) )
			for ( var i = 0; i < key.length; i++ )
				dirty[ key[i] ] = this.__combineDirty( dirty[ key[i] ] || {}, otherDirty[ key[i] ] );
		else
			dirty[ key ] = this.__combineDirty__( dirty[ key ] || {}, otherDirty[ key ] );
	return dirty;
};
CoreModel.prototype.combineDirty = function( otherDirty ) {
	this.__dirty__ = this.__combineDirty__( this.__dirty__ || {}, otherDirty );
};

CoreModel.prototype.__setDirty__ = function( dirty, keys, depth ) {
	if ( dirty === true )
		return true;
	if ( depth >= keys.length )
		return true;
	var key = keys[ depth ];
	if ( Array.isArray( key ) )
		for ( var i = 0; i < key.length; i++ )
			dirty[ key[i] ] = this.__setDirty__( dirty[ key[i] ] || {}, keys, depth + 1 );
	else
		dirty[ key ] = this.__setDirty__( dirty[ key ] || {}, keys, depth + 1 );
	return dirty;
};
CoreModel.prototype.setDirty = function() {
	var keys = Array.prototype.slice.call( arguments );
	this.__dirty__ = this.__setDirty__( this.__dirty__ || {}, keys, 0 );
};

CoreModel.prototype.__isDirty__ = function( dirty, keys, depth ) {
	if ( dirty === true )
		return true;
	if ( depth >= keys.length )
		return true;
	var key = keys[ depth ];
	if ( Array.isArray( key ) ) {
		for ( var i = 0; i < key.length; i++ )
			if ( dirty.hasOwnProperty( key[i] ) )
				if ( this.__isDirty__( dirty[ key[i] ], keys, depth + 1 ) )
					return true;
	}
	else {
		if ( dirty.hasOwnProperty( key ) )
			if ( this.__isDirty__( dirty[ key ], keys, depth + 1 ) )
				return true;
	}
	return false;
};
CoreModel.prototype.isDirty = function() {
	var keys = Array.prototype.slice.call( arguments );
	if ( this.hasOwnProperty( "__dirty__" ) )
		return this.__isDirty__( this.__dirty__, keys, 0 );
	else
		return false;
};

CoreModel.prototype.__getDirty__ = function( dirty, keys, depth ) {
	if ( dirty === true )
		return dirty;
	if ( depth >= keys.length )
		return dirty;
	var key = keys[ depth ];
	if ( Array.isArray( key ) ) {
		var results = {};
		for ( var i = 0; i < key.length; i++ )
			if ( dirty.hasOwnProperty( key[i] ) )
				results[ key[i] ] = this.__getDirty__( dirty[ key[i] ], keys, depth + 1 );
			else
				results[ key[i] ] = undefined;
		return results;
	}
	else {
		if ( dirty.hasOwnProperty( key ) )
			return this.__getDirty__( dirty[ key ], keys, depth + 1 );
		else
			return undefined;
	}
};
CoreModel.prototype.getDirty = function() {
	var keys = Array.prototype.slice.call( arguments );
	if ( this.hasOwnProperty( "__dirty__" ) )
		return this.__getDirty__( this.__dirty__, keys, 0 );
	else
		return undefined;
};

CoreModel.prototype.__setAttribute__ = function( attribute, keys, depth, value ) {
	var key = keys[ depth ];
	if ( Array.isArray( key ) ) {
		for ( var i = 0; i < key.length; i++ )
			if ( depth + 1 >= keys.length )
				if ( value === undefined )
					delete attribute[ key[i] ];
				else
					attribute[ key[i] ] = value;
			else
				if ( attribute.hasOwnProperty( key[i] ) )
					attribute[ key[i] ] = this.__setAttribute__( attribute[ key[i] ], keys, depth + 1, value );
				else
					attribute[ key[i] ] = this.__setAttribute__( {}, keys, depth + 1, value );
	}
	else {
		if ( depth + 1 >= keys.length )
			if ( value === undefined )
				delete attribute[ key ];
			else
				attribute[ key ] = value;
		else
			if ( attribute.hasOwnProperty( key ) )
				attribute[ key ] = this.__setAttribute__( attribute[ key ], keys, depth + 1, value );
			else
				attribute[ key ] = this.__setAttribute__( {}, keys, depth + 1, value );
	}
	return attribute;
};
CoreModel.prototype.setAttribute = function() {
	var keys = Array.prototype.slice.call( arguments );
	var value = keys.pop();
	var key = keys[ 0 ];
	if ( Array.isArray( key ) ) {
		for ( var i = 0; i < key.length; i++ )
			if ( 1 >= keys.length )
				if ( value === undefined )
					this.unset( key[i], { "silent" : true } );
				else
					this.set( key[i], value, { "silent" : true } );
			else
				this.set( key[i], this.__setAttribute__( this.get( key[i] ) || {}, keys, 1, value ), { "silent" : true } );
	}
	else {
		if ( 1 >= keys.length )
			if ( value === undefined )
				this.unset( key, { "silent" : true } );
			else
				this.set( key, value, { "silent" : true } );
		else
			this.set( key, this.__setAttribute__( this.get( key ) || {}, keys, 1, value ), { "silent" : true } );
	}
	return this;
};

CoreModel.prototype.__hasAttribute__ = function( attribute, keys, depth ) {
	var key = keys[ depth ];
	if ( Array.isArray( key ) ) {
		for ( var i = 0; i < key.length; i++ )
			if ( ! attribute.hasOwnProperty( key[i] ) )
				return false;
			else if ( depth + 1 < keys.length && ! this.__hasAttribute__( attribute[ key[i] ], keys, depth + 1 ) )
				return false;
	}
	else {
		if ( ! attribute.hasOwnProperty( key ) )
			return false;
		else if ( depth + 1 < keys.length && ! this.__hasAttribute__( attribute[ key ], keys, depth + 1 ) )
			return false;
	}
	return true;
};
CoreModel.prototype.hasAttribute = function() {
	var keys = Array.prototype.slice.call( arguments );
	var key = keys[ 0 ];
	if ( Array.isArray( key ) ) {
		for ( var i = 0; i < key.length; i++ )
			if ( ! this.has( key[i] ) )
				return false;
			else if ( 1 < keys.length && ! this.__hasAttribute__( this.get( key[i] ), keys, 1 ) )
				return false;
	}
	else {
		if ( ! this.has( key ) )
			return false;
		else if ( 1 < keys.length && ! this.__hasAttribute__( this.get( key ), keys, 1 ) )
			return false;
	}
	return true;
};

CoreModel.prototype.__getAttribute__ = function( attribute, keys, depth ) {
	var key = keys[ depth ];
	if ( Array.isArray( key ) ) {
		var results = {};
		for ( var i = 0; i < key.length; i++ )
			if ( depth + 1 >= keys.length )
				if ( attribute.hasOwnProperty( key[i] ) )
					results[ key[i] ] = attribute[ key[i] ];
				else
					results[ key[i] ] = undefined;
			else
				if ( attribute.hasOwnProperty( key[i] ) )
					results[ key[i] ] = this.__getAttribute__( attribute[ key[i] ], keys, depth + 1 );
				else
					results[ key[i] ] = undefined;
		return results;
	}
	else {
		if ( depth + 1 >= keys.length )
			if ( attribute.hasOwnProperty( key ) )
				return attribute[ key ];
			else
				return undefined;
		else
			if ( attribute.hasOwnProperty( key ) )
				return this.__getAttribute__( attribute[ key ], keys, depth + 1 );
			else
				return undefined;
	}
};
CoreModel.prototype.getAttribute = function() {
	var keys = Array.prototype.slice.call( arguments );
	var key = keys[ 0 ];
	if ( Array.isArray( key ) ) {
		var results = {};
		for ( var i = 0; i < key.length; i++ )
			if ( 1 >= keys.length )
				if ( this.has( key[i] ) )
					results[ key[i] ] = this.get( key[i] );
				else
					results[ key[i] ] = undefined;
			else
				if ( this.has( key[i] ) )
					results[ key[i] ] = this.__getAttribute__( this.get( key[i] ), keys, 1 );
				else
					results[ key[i] ] = undefined;
		return results;
	}
	else {
		if ( 1 >= keys.length )
			if ( this.has( key ) )
				return this.get( key );
			else
				return undefined;
		else
			if ( this.has( key ) )
				return this.__getAttribute__( this.get( key ), keys, 1 );
			else
				return undefined
	}
};
