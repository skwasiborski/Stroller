/**
 * Sample React Native App
 * https://github.com/facebook/react-native
 *
 * @format
 * @flow strict-local
 */
import 'react-native-gesture-handler';
import React, { useState, useRef, useEffect } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  StatusBar,
  Dimensions, 
  Alert, 
  ActivityIndicator,
  Button, 
  TouchableHighlight,
  Image,
  TextInput
} from 'react-native';

import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

import buffer from 'buffer'

import Geolocation from '@react-native-community/geolocation';

import { RNCamera } from 'react-native-camera';

function timeoutPromise(ms, promise) {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error("promise timeout"))
    }, ms);
    promise.then(
      (res) => {
        clearTimeout(timeoutId);
        resolve(res);
      },
      (err) => {
        clearTimeout(timeoutId);
        reject(err);
      }
    );
  })
}

const CaptureButton: ({buttonDisabled: bool, onClick: () => mixed}) => React$Node = (props) => {
  return (
    <TouchableHighlight 
      style={{
        marginBottom:30,
        width:160,
        borderRadius:10,
        backgroundColor: "white",
        alignSelf: "center"
      }} 
      disabled={props.buttonDisabled}>
      <Button onPress={props.onClick} disabled={props.buttonDisabled} title="Capture" accessibilityLabel="Learn more about this button"/>
    </TouchableHighlight>
  );
};

const LoadableLabeledTextInput: ({onTextChanged: string => mixed, value: string, label: string, loading: bool}) => React$Node = (props) => {
  return (
    <View
      style={{
        flexDirection: 'row',
        height: 30,
        margin: 10
      }}>
      <View
        style={{
          justifyContent: 'center',
          alignItems: 'center'
        }}>
        <Text style={{ marginRight: 10, width: 110}}>{props.label}</Text>
      </View>
      <View style={{flex: 1}}>
        <TextInput
          style={{ borderColor: 'gray', padding: 3, borderWidth: 1, flex: 1}}
          onChangeText={text => props.onTextChanged(text)}
          value={props.value}
        />
        {props.loading && 
        <ActivityIndicator 
          size="small" 
          animating={true}
          color="#fff" 
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.2)',
            
          }}/>
        }
      </View>
    </View>
  )
}

const DetailsScreen: ({ route : any, navigation: any }) => React$Node = ({ route, navigation }) => {
  const [address, setAddress] = React.useState('');
  const [licensePlate, setLicensePlate] = React.useState('');
  const [plateLoaded, setPlateLoaded] = React.useState(false);
  const [addressLoaded, setAddressLoaded] = React.useState(false);
  const [imageSize, setImageSize] = React.useState({width: Dimensions.get('window').width, height: Dimensions.get('window').height/2.5});

  useEffect(() => {
    Image.getSize(route.params.data.uri, (width, height) => {
        const windowWidth= Dimensions.get('window').width;
        setImageSize({width: windowWidth, height: windowWidth/width * height});
      });
  }, [route.params.data.uri]);

  useEffect(() => {
    const fetchAddress = async () => { 
      try {
        const geo = await new Promise((resolve, reject) => Geolocation.getCurrentPosition(info => resolve(info), err => reject(err)));
        const response = await fetch(`https://mobile.um.warszawa.pl/cxf/bgik/rest/nearestPoint?latitude=${geo.coords.latitude}&longitude=${geo.coords.longitude}`);
        const addr = await response.json();
        setAddress(`${addr.address} ${addr.postalCode}`);
      } finally {
        setAddressLoaded(true);
      }
    };

    fetchAddress();
  }, []);  

  useEffect(() => {
    const fetchLicensePlate = async () => { 
      try {
        const img = route.params.data.base64;
        const response = await timeoutPromise(20000, fetch(
            "https://stroller.azurewebsites.net/api/getplate?code=A9WwRfqqpYNNCjllWOVERLXsrIh/heRM9xzZ3uVwnwOceIDPOpW0jA==", 
            {
              method: 'POST',
              headers: {
              'Content-Type': 'image/jpeg; charset=utf-8',
            },
            body: buffer.Buffer.from(img, 'base64'),
          }));

        const plateResponse = await response.text();
        setLicensePlate(plateResponse);
      } finally {
        setPlateLoaded(true);
      }
    };

    fetchLicensePlate();
  }, []);  

  return (
    <View 
      style={{
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'stretch',
        justifyContent: 'flex-start',	
      }}> 
      <ScrollView style={{ flex: 1 }}>
        <Image
          style={{
            height: imageSize.height,
            width: imageSize.width,
            resizeMode: 'contain',
          }}
          source={{ uri: route.params.data.uri }}
        />
      </ScrollView>
      <View
        style={{
          flex: 2
        }}>
        <LoadableLabeledTextInput label="Adres:" 
                                  value={address} 
                                  onTextChanged={setAddress}
                                  loading={!addressLoaded} />
        <LoadableLabeledTextInput label="Nr rejestracyjny:" 
                                  value={licensePlate} 
                                  onTextChanged={setLicensePlate}
                                  loading={!plateLoaded} />
        
      </View>
    </View>
  );
};

const CameraScreen: ({ navigation: any }) => React$Node = ({ navigation }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [identifiedAs, setIdentifiedAs] = useState("");

  const camera = useRef(null);

  const takePicture = async function() {
    let cam = camera.current;
		if (cam) {
      setIsLoading(true);
			const data = await cam.takePictureAsync({ quality: 0.001, base64: true });
      cam.pausePreview();
      setIdentifiedAs("identifiedImage");
      setIsLoading(false);

      if (camera.current) {
        camera.current.resumePreview();
      }
      navigation.navigate('Details', { data: data })
		}
	}

  return (
    <View style={{
            flex: 1,
            backgroundColor: '#fff',
          }}>
      <RNCamera ref={camera} 
                style={{
                  flex: 1,
                }} 
                captureAudio={false}>
        <ActivityIndicator 
          size="large" 
          style={{
            flex: 1,
            alignItems: 'center',
            justifyContent: 'center',
          }} 
          color="#fff" 
          animating={isLoading}/>
        <CaptureButton buttonDisabled={isLoading} onClick={takePicture}/>
      </RNCamera>
    </View>
  );
};

const Stack = createStackNavigator();

const App: () => React$Node = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen name="Home" component={CameraScreen} />
        <Stack.Screen name="Details" component={DetailsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;